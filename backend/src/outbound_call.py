import asyncio
import os
import sys
import argparse
from dotenv import load_dotenv
from livekit.api import LiveKitAPI, CreateSIPParticipantRequest, CreateAgentDispatchRequest

# Load environment variables from .env.local
load_dotenv(".env.local")

async def main():
    parser = argparse.ArgumentParser(description="Initiate outbound SIP call")
    parser.add_argument("--item", default="Test Item", help="Item name")
    parser.add_argument("--qty", default="1", help="Quantity")
    parser.add_argument("--price", default="0", help="Price")
    args = parser.parse_args()

    api_key = os.environ.get("LIVEKIT_API_KEY")
    api_secret = os.environ.get("LIVEKIT_API_SECRET")
    lk_url = os.environ.get("LIVEKIT_URL")
    sip_uri = os.environ.get("LINPHONE_SIP_URI")
    # If the URI is sip:user@host, extract just the user part
    if sip_uri and sip_uri.startswith("sip:"):
        # Remove 'sip:' and split at '@'
        sip_user = sip_uri[4:].split("@")[0]
    else:
        sip_user = sip_uri
    
    trunk_id = os.environ.get("LIVEKIT_SIP_TRUNK_ID")

    if not all([api_key, api_secret, lk_url, sip_user, trunk_id]):
        print(f"Missing or invalid required environment variables: {api_key=}, {api_secret=}, {lk_url=}, {sip_user=}, {trunk_id=}")
        sys.exit(1)

    # Use a unique room name for this call
    import time
    room_name = f"outbound-{args.item.replace(' ', '-')}-{int(time.time())}"
    metadata = f"order: {args.item}, qty: {args.qty}, price: {args.price}"

    async with LiveKitAPI(lk_url, api_key, api_secret) as api:
        print(f"Dialing {sip_user} via trunk {trunk_id}...")
        try:
            await api.sip.create_sip_participant(
                CreateSIPParticipantRequest(
                    sip_trunk_id=trunk_id,
                    sip_call_to=sip_user,
                    room_name=room_name,
                    participant_identity="VyapaarMitraAgent",
                    participant_metadata=metadata,
                )
            )
            print(f"Call initiated. Room: {room_name}")

            # Dispatch the agent into this room
            await api.agent_dispatch.create_dispatch(
                CreateAgentDispatchRequest(
                    agent_name="my-agent",
                    room=room_name,
                    metadata=metadata,
                )
            )
            print(f"Agent dispatched to room: {room_name}")
        except Exception as e:
            print(f"Failed to initiate call: {e}")

if __name__ == "__main__":
    asyncio.run(main())
