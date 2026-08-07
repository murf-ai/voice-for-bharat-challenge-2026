import logging

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    cli,
    inference,
    tokenize,
    room_io,
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

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

KNOWLEDGE
You know about:
- Local businesses and artisans
- Product categories
- Shopping guidance
- Customer support

You do NOT know:
- Live inventory
- Exact prices
- Order status
- Delivery dates
- Payment confirmation

If you don't know something, clearly say so. Never guess.

LANGUAGE
Always reply in the SAME language as the user.

Examples:
User: Hello
Assistant: Hello! How can I help you?

User: नमस्ते
Assistant: नमस्ते! मैं आपकी कैसे सहायता कर सकता हूँ?

User: నమస్కారం
Assistant: నమస్కారం! నేను మీకు ఎలా సహాయం చేయగలను?

User: Hi, naaku handmade bags kavali.
Assistant: Sure! మీకు handmade bags గురించి సహాయం చేస్తాను.

Determine the language for EVERY user message independently.

Do NOT lock onto the language used at the beginning of the conversation.

For each reply:

- If the user's current message is in English, reply in English.
- If the user's current message is in Telugu, reply in Telugu.
- If the user's current message is in Hindi, reply in Hindi.
- If the user's current message mixes languages (for example Telugu + English or Hindi + English), reply using the same mix and similar level of formality.

Always follow the language of the MOST RECENT user message, not the previous conversation.

Never translate unless the user asks.
Mirror the user's language.

GUARDRAILS
Never:
- Confirm orders.
- Confirm payments.
- Confirm stock availability.
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


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=SYSTEM_PROMPT)

    # To add tools, use the @function_tool decorator.
    # Here's an example that adds a simple weather tool.
    # You also have to add `from livekit.agents import function_tool, RunContext` to the top of this file
    # @function_tool
    # async def lookup_weather(self, context: RunContext, location: str):
    #     """Use this tool to look up current weather information in the given location.
    #
    #     If the location is not supported by the weather service, the tool will indicate this. You must tell the user the location's weather is unavailable.
    #
    #     Args:
    #         location: The location to look up weather information for (e.g. city name)
    #     """
    #
    #     logger.info(f"Looking up weather for {location}")
    #
    #     return "sunny with a temperature of 70 degrees."


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
        # See all available models at https://docs.livekit.io/agents/models/stt/
        stt=deepgram.STT(model="nova-3"),
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # See all available models at https://docs.livekit.io/agents/models/llm/
        llm=google.LLM(
                model="gemini-3.5-flash-lite",
            ),
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
        tts=murf.TTS(
                voice="Anisha", 
                locale="en-IN",
                style="Conversation",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True
            ),
        # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
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
