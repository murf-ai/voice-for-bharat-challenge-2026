# Day 2 – Give Your Agent a Personality, a Job, and Limits

Yesterday your agent could talk. Today it becomes _someone_: with a job it's good at, and a list of things it will refuse to do.

For Day 2, your objective is to:

- **Step 1: Define 2–3 call objectives.** What does a successful call achieve?

- **Step 2: Write your guardrails.** At minimum: what the agent must **refuse**, what it must **never claim**, and its **escalation script**.

  Examples of guardrails your track needs:

  | Track               | Example                                                                            |
  | ------------------- | ---------------------------------------------------------------------------------- |
  | Farm & Field        | Never state a market price as current fact without a source and date               |
  | Health Access       | Never diagnose or name a prescription drug; escalate red-flag symptoms to a doctor |
  | Learning & Literacy | Never shame a wrong answer; never claim a child has a learning disability          |
  | Local Commerce      | Never confirm an order, price or delivery date the seller hasn't set               |
  | Financial Services  | Never ask for OTP, PIN or account number; never promise scheme approval            |
  | Disaster Response   | Never issue an all-clear or evacuation instruction on its own authority            |

- **Step 3: Verify code-mixed language support.** Verify that your agent can handle a user who starts in Hindi, drops in English words, and expects a reply in the same register or speaks in a different language entirely.

- **Step 4: Write a first-turn greeting.**

  Structure your prompt or instructions roughly like this:

  ```
  IDENTITY     who the agent is, who it works for
  OBJECTIVES   what a successful call achieves
  KNOWLEDGE    what it knows, and where that stops
  LANGUAGE     mirror the user's mix; register; formality
  GUARDRAILS   hard refusals, never-claims, escalation script
  STYLE        sentence length, pace, handling silence
  ```

- **Step 5: Successfully connect to your agent** and hold a conversation showing its persona, its job and its limits.

- **Step 6: Record a short video** showing three things: the greeting, a code-mixed exchange, and a guardrail refusing an out-of-scope request.

- **Step 7: Post the video on LinkedIn** with a description of what you built on Day 2. Mention that you're building a voice agent using the fastest TTS API — **Murf Falcon**. Mention that you're part of **10 Days of Voice Agents** and don't forget to tag the official **Murf AI** handle. Also use the hashtag **#VoiceForBharat**.

- **Step 8: Submit your post link on the submission form shared on Discord**

## Advanced (Optional)

You only need the steps above to complete Day 2. These are for going the extra mile:

- **Red-team it.** Write ten prompts designed to break your guardrails — include the boring ones, since a confused user repeating themselves breaks more agents than a clever jailbreak. Commit the results as `RED_TEAM.md`.
- **Handle the silent user.** Add a re-prompt after a few seconds of silence and a graceful close after two failures.
- **Tune for speech, not text.** Read your agent's replies out loud. Anything with a bulleted list, a bracket, or a sentence over ~20 words was written for a screen. Rewrite it.

### You've finished Day 2 if:

- The agent introduces itself and states what it can help with
- It stays on its job across at least three turns
- It handles a code-mixed sentence and replies in a matching register
- You can trigger a guardrail on camera, and the agent declines **and** offers the escalation path

Once your agent is running, your LinkedIn post is live and your form submission is in, you've completed Day 2.

## Resources

- [Prompting Voice Agents](https://docs.livekit.io/agents/start/prompting)
- [Agent Nodes](https://docs.livekit.io/agents/logic/nodes/) — see the "On user turn completed" section
- [Falcon 2 Model Documentation](https://murf.ai/api/docs/text-to-speech-models/falcon-2)
