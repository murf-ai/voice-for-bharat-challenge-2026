'use client';

import { motion } from 'motion/react';
import type { AgentState } from '@livekit/components-react';

interface SpeakerIndicatorProps {
  state?: AgentState;
  userIsSpeaking?: boolean;
}

export function SpeakerIndicator({ state, userIsSpeaking }: SpeakerIndicatorProps) {
  const isUserSpeaking = state === 'listening' || userIsSpeaking;
  const isAgentSpeaking = state === 'speaking';

  if (!isUserSpeaking && !isAgentSpeaking) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.2 }}
      className="flex items-center justify-center gap-2 px-4 py-2 bg-green-100 border border-green-300 rounded-full"
    >
      {isUserSpeaking && (
        <>
          <motion.div
            className="text-lg"
            animate={{ scale: [1, 1.1, 1] }}
            transition={{ duration: 0.6, repeat: Infinity }}
          >
            🎤
          </motion.div>
          <span className="text-sm font-semibold text-green-800">You are speaking</span>
        </>
      )}

      {isAgentSpeaking && (
        <>
          <motion.div
            className="text-lg"
            animate={{ scale: [1, 1.1, 1] }}
            transition={{ duration: 0.6, repeat: Infinity }}
          >
            🤖
          </motion.div>
          <span className="text-sm font-semibold text-green-800">VyapaarMitra is speaking</span>
        </>
      )}
    </motion.div>
  );
}
