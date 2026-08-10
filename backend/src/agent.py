import json
import logging

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    RunContext,
    cli,
    function_tool,
    room_io,
    tokenize,
)
from livekit.plugins import deepgram, google, murf, noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

import db

logger = logging.getLogger("agent")

# Language detection and locale mapping
LANGUAGE_LOCALE_MAP = {
    "telugu": "te-IN",
    "hindi": "hi-IN",
    "english": "en-IN",
}

def detect_language(text: str) -> str:
    """Detect language from text using script detection."""
    if not text:
        return "english"

    # Telugu script detection (Unicode range)
    if any('\u0C00' <= c <= '\u0C7F' for c in text):
        return "telugu"
    # Hindi/Devanagari script detection
    if any('\u0900' <= c <= '\u097F' for c in text):
        return "hindi"

    return "english"

def get_locale_for_language(language: str) -> str:
    """Get TTS locale for detected language."""
    return LANGUAGE_LOCALE_MAP.get(language.lower(), "en-IN")

load_dotenv(".env.local")

# Change this prompt to change what your voice agent does.
# See README.md for example prompts (customer support, language tutor, receptionist).
SYSTEM_PROMPT =  """
IDENTITY
You are VyapaarMitra, an AI voice assistant for India's local businesses, artisans, and small shop owners. You help customers discover products and answer general shopping questions. You work alongside the seller—you are not the seller.

OBJECTIVES
A successful conversation should:
- Understand what the customer needs.
- Help them find suitable products or categories.
- Answer general shopping questions.
- Guide them to the seller whenever confirmation is required.
- End the conversation politely.
- Use caller memory to provide personalized experiences.

KNOWLEDGE
You know about:
- Local businesses and artisans
- Product categories
- Shopping guidance
- Customer support
- Caller's past orders, preferences, and details if available in memory.
- Real-time product search, price, stock, and availability using the `search_products` tool.

You do NOT know:
- Order status
- Delivery dates
- Payment confirmation

If you don't know something, clearly say so. Never guess.

PRODUCT SEARCH & CATALOGUE RULES
1. Always call `search_products` when the user asks about:
   - product availability (e.g., "Do you have iPhone?", "Is coffee available?")
   - product price (e.g., "How much is shampoo?", "What is the price of bags?")
   - ordering a product (e.g., "Order protein powder.", "I want to buy tea.")
   - searching for a product (e.g., "I need cooking oil.", "Show me wireless headphones.")
   - stock information (e.g., "How many units do you have?", "Is it in stock?")
2. Search query translation: If the user asks in Telugu, Hindi, or a mixed language, translate the product search query to English before calling `search_products` to ensure the English-based catalogue is searched successfully.
3. Live Catalogue Responses:
   - Always mention that the data comes from today's live catalogue.
   - Never read raw JSON to the user. Respond naturally in a conversational style.
   - If products are found:
     - If multiple products exist, summarize the top 3 products naturally.
     - Include product name, price (in INR), stock, rating, and availability in your description.
     - Example response for single product: "I found Samsung Galaxy S24. Price is ₹76415. Stock available: 14 units. Rating: 4.8 stars. This information is from today's live catalogue."
   - If the tool returns that no products were found, say exactly:
     "Sorry, I couldn't find that product in today's live catalogue."
   - If the tool returns that the API failed, timed out, or had an error, say exactly:
     "I'm sorry. I couldn't reach today's live product catalogue. Please try again after a few moments."
   - Never hallucinate products or prices not returned by the tool.

LANGUAGE & SCRIPT
CRITICAL: You MUST ALWAYS detect the language and script the user is speaking, and reply in the exact same language and script, unless the user explicitly requests another language.
- English → English script.
- Telugu → తెలుగు script.
- Hindi → देवनागरी script.
- NEVER romanize Telugu or Hindi.
- NEVER mix scripts unless the user intentionally code-mixes.
- If the user speaks Telugu, reply completely in Telugu script.
- If the user speaks Hindi, reply completely in Devanagari.
- If the user speaks English, reply in English.
- If the user mixes languages, naturally match the user's style while keeping each language in its correct script.

PERSONALIZATION & MEMORY RULES:
1. At the start of the conversation, call `lookup_caller` using the `user_id`.
2. If record found, greet by name and mention relevant past facts (e.g., "Namaste Ramesh, last time we spoke about your order of 5kg rice. Should I repeat the same order?").
3. If no record, proceed as a new caller.
4. Before calling `save_caller_info`, YOU MUST ASK PERMISSION OUT LOUD: "I'd like to remember this for next time — is that okay?".
5. If the user says NO to saving, DO NOT call `save_caller_info`.

GUARDRAILS
Never:
- Confirm orders.
- Confirm payments.
- Confirm delivery dates.
- Promise discounts.
- Pretend to be the seller.
- Invent information.

If confirmation is required, say:
"I can't confirm that because only the seller has access to that information. Please contact the seller for confirmation."

If the user asks something unrelated to shopping, politely explain that your role is limited to helping with local shopping and guide the conversation back.

STYLE
Speak like a real person on a phone call.
Be warm, calm, and respectful.
Keep replies short (1-3 sentences).
Avoid bullet points, markdown, emojis, or technical language while speaking.

If the user is silent for a few seconds, ask:
"Are you still there? I'm happy to help whenever you're ready."

Start every new conversation by saying (after calling lookup_caller):
"Hello! I'm VyapaarMitra. I help customers discover products from local businesses and artisans. How can I help you today?"
"""


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=SYSTEM_PROMPT)

    @function_tool
    async def lookup_caller(self, context: RunContext, user_id: str):
        """Use this tool to look up a caller's record in the database.

        Args:
            user_id: The unique identifier for the caller.
        """
        logger.info(f"Looking up caller: {user_id}")
        record = db.lookup_caller(user_id)
        if record:
            return json.dumps(record)
        return "No record found."

    @function_tool
    async def save_caller_info(self, context: RunContext, user_id: str, name: str, language_preference: str, facts: str):
        """Use this tool to save a caller's record in the database.

        Args:
            user_id: The unique identifier for the caller.
            name: The caller's name.
            language_preference: The caller's preferred language (e.g., 'English', 'Telugu').
            facts: A JSON string containing facts about the caller (e.g., '{"past_orders": ["rice"], "usual_quantities": ["5kg"]}').
        """
        logger.info(f"Saving caller info for: {user_id}")
        facts_dict = json.loads(facts)
        db.save_caller_info(user_id, name, language_preference, facts_dict)
        return "Caller information saved successfully."

    @function_tool
    async def search_products(self, context: RunContext, query: str) -> str:
        """Use this tool to search for products in today's live catalogue when the user asks about product availability, price, stock, ordering, or searching for a product.

        Args:
            query: The name, keyword, or category of the product to search for (e.g., 'iPhone', 'oil', 'shampoo').
        """
        logger.info(f"Searching products for query: {query}")
        try:
            import asyncio
            import urllib.parse
            import urllib.request

            url = f"https://dummyjson.com/products/search?q={urllib.parse.quote(query)}"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )

            loop = asyncio.get_running_loop()

            def _fetch():
                with urllib.request.urlopen(req, timeout=5) as response:
                    return response.read().decode("utf-8")

            response_text = await loop.run_in_executor(None, _fetch)
            data = json.loads(response_text)

            products = data.get("products", [])
            if not products:
                return json.dumps({"products": [], "status": "no_results"})

            # Keep only the top 3 products
            top_products = products[:3]
            parsed_products = []
            for p in top_products:
                price_usd = p.get("price", 0)
                price_inr = round(price_usd * 85)
                parsed_products.append({
                    "product_name": p.get("title"),
                    "brand": p.get("brand", "Unknown"),
                    "price": f"₹{price_inr}",
                    "stock": p.get("stock"),
                    "rating": p.get("rating"),
                    "category": p.get("category"),
                    "availability": p.get("availabilityStatus", "In Stock" if p.get("stock", 0) > 0 else "Out of Stock")
                })

            return json.dumps({"products": parsed_products, "status": "success"})

        except Exception as e:
            logger.error(f"Error calling search products API: {e}")
            return json.dumps({"products": [], "status": "error", "message": str(e)})


server = AgentServer()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline using Murf Falcon, Gemini, Deepgram, and the LiveKit turn detector
    session = AgentSession(
        # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
        # Deepgram nova-3 supports multilingual recognition (Telugu, Hindi, English, etc.)
        # See all available models at https://docs.livekit.io/agents/models/stt/
        stt=deepgram.STT(
            model="nova-3",
            language="multi",
        ),
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # Gemini 3.5 Flash Lite supports Telugu, Hindi, English and code-mixing
        # See all available models at https://docs.livekit.io/agents/models/llm/
        llm=google.LLM(
            model="gemini-3.5-flash-lite",
        ),
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
        tts=murf.TTS(
            voice="Anisha",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True
        ),
        # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
        # MultilingualModel supports Telugu, Hindi, English
        # See more at https://docs.livekit.io/agents/build/turns
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # allow the LLM to generate a response while waiting for the end of turn
        # See more at https://docs.livekit.io/agents/build/audio/#preemptive-generation
        preemptive_generation=True,
    )

    # To use a realtime model instead of a voice pipeline, use the following session setup instead.
    # (Note: This is for the OpenAI Realtime API. For other providers, see https://docs.livekit.io/agents/models/realtime/))
    # 1. Install livekit-agents[openai]
    # 2. Set OPENAI_API_KEY in .env.local
    # 3. Add `from livekit.plugins import openai` to the top of this file
    # 4. Use the following session setup instead of the version above
    # session = AgentSession(
    #     llm=openai.realtime.RealtimeModel(voice="marin")
    # )

    # # Add a virtual avatar to the session, if desired
    # # For other providers, see https://docs.livekit.io/agents/models/avatar/
    # avatar = hedra.AvatarSession(
    #   avatar_id="...",  # See https://docs.livekit.io/agents/models/avatar/plugins/hedra
    # )
    # # Start the avatar and wait for it to join
    # await avatar.start(session, room=ctx.room)

    # Start the session, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: (
                    noise_cancellation.BVCTelephony()
                    if params.participant.kind
                    == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                    else noise_cancellation.BVC()
                ),
            ),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(server)
