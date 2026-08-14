import json
import logging
import os
import secrets
import string
import requests
from datetime import datetime

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
1. Caller memory (if any) is provided to you directly in your
instructions at the start of the call -- you do not need to call
lookup_caller yourself unless a different user_id is mentioned
mid-call.
2. If a record was found, greet by name and mention relevant past facts.
If no record was found, proceed as a new caller.
3. Before calling `save_caller_info`, YOU MUST ASK PERMISSION OUT LOUD: "I'd like to remember this for next time — is that okay?".
4. If the user says NO to saving, DO NOT call `save_caller_info`.

HUMAN ESCALATION RULES:
1. If the caller wants a return, refund, exchange, or has an order dispute, ALWAYS call
   `escalate_to_returns_specialist` first — do NOT call `create_escalation` for these cases.
   The Returns and Refunds Specialist handles them directly.
2. ONLY call `create_escalation` when:
   - The Returns Specialist has already been involved and still couldn't resolve it, OR
   - The caller asks something genuinely outside your knowledge or capability that has
     nothing to do with returns/refunds/orders.
3. A normal conversation (stock, product search, general order placement) must NEVER
   trigger either tool.
4. The escalation summary must only include:
   - Who needs help (name/user_id if known from memory)
   - What happened (short description)
   - What the agent already checked/tried
   - Urgency (low/medium/high — pick based on context)
   - Caller's language preference and preferred follow-up method (call back / message)
5. NEVER include passwords, OTPs, PINs, account numbers, or other sensitive data in any escalation.

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

Start every new conversation by saying:
"Hello! I'm VyapaarMitra. I help customers discover products from local businesses and artisans. How can I help you today?"
"""



class ReturnsRefundsSpecialist(Agent):
    def __init__(self, chat_ctx, room=None) -> None:
        instructions = (
            "You are a Returns and Refunds Specialist for VyapaarMitra. "
            "You are exclusively responsible for assisting customers with returns, "
            "refunds, exchanges, and order disputes. "
            "Be polite, professional, and efficient. "
            "If you cannot resolve an issue, guide them to human support via the main agent."
        )
        tts = murf.TTS(
            voice="Samar",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True
        )
        super().__init__(instructions=instructions, chat_ctx=chat_ctx, tts=tts)
        self.room = room

    async def on_enter(self) -> None:
        await self.session.generate_reply(
            instructions="Introduce yourself as the Returns and Refunds Specialist. Ask how you can help with their order, return, or refund."
        )

    @function_tool
    async def return_to_main_agent(self, context: RunContext):
        """Transfer the conversation back to the main Assistant agent."""
        await context.session.say("I'll pass you back to our main assistant now. They can help you with other questions.")

        await self.room.local_participant.publish_data(
            json.dumps({"type": "agent_switch", "agent": "main", "label": "Main Agent"}).encode("utf-8")
        )

        return Assistant(chat_ctx=self.chat_ctx, room=self.room)


class Assistant(Agent):
    def __init__(self, order_details: str = None, caller_record: dict = None, chat_ctx: "llm.ChatContext" = None, room=None) -> None:
        if chat_ctx:
            # We are taking over an existing context
            instructions = SYSTEM_PROMPT
        elif caller_record:
            caller_context = f"The caller has a saved record: {json.dumps(caller_record)}. Greet them by name using relevant facts, and Do NOT call lookup_caller again for this caller -- you already have their info."
            instructions = f"{SYSTEM_PROMPT}\n\n{caller_context}"
        else:
            caller_context = "No record found for this caller. Treat them as a new caller. Do NOT call lookup_caller -- there is nothing to look up."
            instructions = f"{SYSTEM_PROMPT}\n\n{caller_context}"

        if order_details and not chat_ctx:
            outbound_greeting = f"This is VyapaarMitra, your local shop's voice assistant. I am calling to confirm your recent order: {order_details}. If this isn't a good time, just say so and I'll call back later."
            instructions = f"{instructions}\n\nCRITICAL: You are currently on an outbound call. Your FIRST response MUST be exactly: '{outbound_greeting}'"
            
        super().__init__(instructions=instructions, chat_ctx=chat_ctx)
        self.order_details = order_details
        self.call_outcome_success = False
        self.room = room

    @function_tool
    async def escalate_to_returns_specialist(self, context: RunContext):
        """Transfer the conversation to the Returns and Refunds Specialist.
    Call this IMMEDIATELY whenever the caller mentions a return, refund, exchange,
    damaged/wrong item, or wants to dispute an order — before considering create_escalation."""
        try:
            await context.session.say("I understand. I'm connecting you to our returns and refunds specialist who can better assist you with this.")

            await self.room.local_participant.publish_data(
                json.dumps({"type": "agent_switch", "agent": "returns_specialist", "label": "Returns Specialist"}).encode("utf-8")
            )

            return ReturnsRefundsSpecialist(chat_ctx=self.chat_ctx, room=self.room)
        except Exception as e:
            logger.error(f"FAILED to switch to returns specialist: {e}", exc_info=True)
            raise


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
    async def save_order(self, context: RunContext, user_id: str, item: str, quantity: str, price: str):
        """Use this tool to save a user's order in the caller's facts.

        Args:
            user_id: The unique identifier for the caller.
            item: The name of the product being ordered.
            quantity: The quantity of the product.
            price: The price of the product.
        """
        logger.info(f"Saving order in facts for user {user_id}: {item} x {quantity}")
        try:
            # 1. Lookup caller
            record = db.lookup_caller(user_id)
            if not record:
                # If no record, start with empty facts and default name/language
                name = "Unknown"
                language_preference = "English"
                facts = {}
            else:
                name = record['name']
                language_preference = record['language_preference']
                facts = record['facts']

            # 2. Merge order info
            if "orders" not in facts:
                facts["orders"] = []
            facts["orders"].append({
                "item": item,
                "quantity": quantity,
                "price": price,
                "timestamp": datetime.now().isoformat()
            })

            # 3. Save caller info
            db.save_caller_info(user_id, name, language_preference, facts)
            return "Order saved to facts successfully."
        except Exception as e:
            logger.error(f"Error saving order to facts: {e}")
            return f"Failed to save order to facts: {e}"

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
                self.call_outcome_success = True
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

    @function_tool
    async def create_escalation(
        self,
        context: RunContext,
        user_id: str,
        caller_name: str,
        what_happened: str,
        checked_tried: str,
        urgency: str,
        language_preference: str,
        follow_up_method: str,
    ) -> str:
        """Create a human escalation request when a caller has an unresolved payment, refund,
        or order dispute, or when they ask something genuinely outside your knowledge or capability.
        Before calling this tool, you must ask the caller's permission out loud, tell them
        a short summary of what is shared, and proceed only if they say yes.

        Args:
            user_id: The unique identifier of the caller.
            caller_name: The name of the caller (if known from memory, otherwise 'Unknown').
            what_happened: A short description of the issue or dispute.
            checked_tried: What you (the agent) already checked or tried during the call.
            urgency: The urgency level. Must be 'low', 'medium', or 'high' based on context.
            language_preference: The caller's language preference (e.g., 'English', 'Telugu', 'Hindi').
            follow_up_method: The caller's preferred method for follow-up ('call back' or 'message').
        """
        logger.info(f"Creating escalation for user {user_id} ({caller_name})")

        # Generate 6-char alphanumeric reference ID
        alphabet = string.ascii_uppercase + string.digits
        reference_id = "".join(secrets.choice(alphabet) for _ in range(6))

        # Check webhook URL
        webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        if not webhook_url:
            logger.error("DISCORD_WEBHOOK_URL environment variable is not set.")
            return "I'm having trouble sending this request right now, please try again in a few minutes."

        # Map color based on urgency
        color_map = {
            "high": 0xDC143C,    # Crimson/Red
            "medium": 0xFFA500,  # Orange
            "low": 0x228B22,     # Forest Green
        }
        color = color_map.get(urgency.lower(), 0x808080)

        # Structure the fields of the Discord embed
        fields = [
            {"name": "Reference ID", "value": reference_id, "inline": True},
            {"name": "Caller Name", "value": caller_name if caller_name else "Unknown", "inline": True},
            {"name": "User ID", "value": user_id if user_id else "Unknown", "inline": True},
            {"name": "What Happened", "value": what_happened if what_happened else "Not specified", "inline": False},
            {"name": "What Checked/Tried", "value": checked_tried if checked_tried else "Not specified", "inline": False},
            {"name": "Urgency", "value": urgency.upper() if urgency else "LOW", "inline": True},
            {"name": "Language Preference", "value": language_preference if language_preference else "Unknown", "inline": True},
            {"name": "Preferred Follow-up", "value": follow_up_method if follow_up_method else "Not specified", "inline": True},
        ]

        # Make sure values are not empty or only whitespace as Discord API throws bad request on empty embed fields
        for field in fields:
            if not field["value"] or str(field["value"]).strip() == "":
                field["value"] = "Not Provided"

        payload = {
            "embeds": [
                {
                    "title": f"🚨 Human Escalation - Ref: {reference_id}",
                    "color": color,
                    "fields": fields
                }
            ]
        }

        try:
            # Run blocking request in an executor
            import asyncio
            loop = asyncio.get_running_loop()

            def _send():
                response = requests.post(webhook_url, json=payload, timeout=5)
                response.raise_for_status()
                self.call_outcome_success = True
                return response

            await loop.run_in_executor(None, _send)

        except Exception as e:
            logger.error(f"Error calling Discord webhook: {e}")
            return "I'm having trouble sending this request right now, please try again in a few minutes."

        return f"Successfully created escalation. Reference ID: {reference_id}. Someone from the team will follow up, usually within a few hours — I can't guarantee an immediate reply."


server = AgentServer()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: JobContext):
    logger.info(f"Agent triggered for room: {ctx.room.name}")
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
    # Join the room and connect to the user
    await ctx.connect()

    # Detect outbound call via metadata
    order_details = None
    for participant in ctx.room.remote_participants.values():
        logger.info(f"Participant {participant.identity} metadata: {participant.metadata}")
        if participant.metadata and "order:" in participant.metadata:
            order_details = participant.metadata
            break

    caller_record = db.lookup_caller(user_id="default_user")

    # Determine channel
    channel = "sip" if any(p.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP for p in ctx.room.remote_participants.values()) else "browser"
    db.create_call_record(call_sid=ctx.room.name, channel=channel)

    # Instantiate the agent to track outcome, but pass the class to session.start
    assistant_instance = Assistant(order_details=order_details, caller_record=caller_record, room=ctx.room)

    async def on_shutdown():
        db.update_call_outcome(
            call_sid=ctx.room.name,
            outcome="success" if assistant_instance.call_outcome_success else "failed",
            failure_reason=None if assistant_instance.call_outcome_success else "no_success_condition_met",
        )

    ctx.add_shutdown_callback(on_shutdown)

    # Start the session, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=assistant_instance,
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


    if order_details:
        # Outbound calls: the agent must speak first
        await session.generate_reply(
            instructions=(
                "Greet the caller now. Say who you are (VyapaarMitra, their local shop's "
                "voice assistant), why you're calling (to confirm their recent order), "
                "and that they can say 'stop' or 'not now' at any time to end the call. "
                "Then mention the order details naturally."
            )
        )
    else:
        # Inbound/browser sessions: greet normally, using context provided in instructions
        await session.generate_reply(
            instructions="Greet the caller now as VyapaarMitra, using any caller memory context you have."
        )


if __name__ == "__main__":
    cli.run_app(server)
