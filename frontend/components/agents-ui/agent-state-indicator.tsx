'use client';

import { motion, AnimatePresence } from 'motion/react';
import type { AgentState } from '@livekit/components-react';
import { Button } from '@/components/ui/button';

interface AgentStateIndicatorProps {
  state?: AgentState;
  requestHandle?: 'microphone_permission' | null;
  onStartNewConversation?: () => void;
}

export function AgentStateIndicator({
  state,
  requestHandle,
  onStartNewConversation,
}: AgentStateIndicatorProps) {
  const getStateContent = () => {
    switch (state) {
      case 'disconnected':
        return {
          emoji: '✅',
          title: 'Ready',
          message: 'Ready to start your voice shopping experience.',
          showButton: false,
        };

      case 'connecting':
      case 'initializing':
        return {
          emoji: '⏳',
          title: 'Connecting',
          message: 'Connecting to VyapaarMitra...',
          submessage: 'Please wait while we prepare your assistant.',
          showButton: false,
          isLoading: true,
        };

      case 'listening':
        return {
          emoji: '🎤',
          title: 'Listening',
          message: "I'm listening to you.",
          submessage: 'Please go ahead and speak.',
          showButton: false,
        };

      case 'thinking':
        return {
          emoji: '🤔',
          title: 'Processing',
          message: 'Processing your request...',
          submessage: 'VyapaarMitra is thinking.',
          showButton: false,
          isLoading: true,
        };

      case 'speaking':
        return {
          emoji: '🗣️',
          title: 'Speaking',
          message: 'VyapaarMitra is speaking...',
          submessage: 'Please wait for the response.',
          showButton: false,
        };

      case 'failed':
        return {
          emoji: '❌',
          title: 'Connection Failed',
          message: 'The call has ended unexpectedly.',
          showButton: true,
          buttonText: '🔄 Start New Conversation',
        };

      default:
        return {
          emoji: '🎧',
          title: 'Ready',
          message: 'Ready to start your voice shopping experience.',
          showButton: false,
        };
    }
  };

  const content = getStateContent();

  // Show microphone permission error if needed
  if (requestHandle === 'microphone_permission') {
    return (
      <AnimatePresence>
        <motion.div
          key="mic-error"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="flex flex-col items-center justify-center gap-4 px-6 py-8 bg-red-50 border-2 border-red-200 rounded-xl max-w-md"
        >
          <div className="text-4xl">🎤❌</div>
          <h3 className="text-xl font-bold text-red-900">Microphone Access Required</h3>
          <p className="text-center text-red-800">
            VyapaarMitra needs microphone access to hear your voice. Please allow microphone
            permission in your browser settings and refresh the page.
          </p>
          <Button
            onClick={() => window.location.reload()}
            className="mt-2 bg-red-600 hover:bg-red-700 text-white font-semibold px-6 py-2 rounded-lg"
          >
            Retry Microphone Access
          </Button>
        </motion.div>
      </AnimatePresence>
    );
  }

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={state || 'default'}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        transition={{ duration: 0.3 }}
        className="flex flex-col items-center justify-center gap-3"
      >
        <div className="text-4xl md:text-5xl">{content.emoji}</div>

        <div className="text-center">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-900">{content.title}</h2>
          <p className="text-lg text-gray-700 mt-2">{content.message}</p>
          {content.submessage && <p className="text-sm text-gray-600 mt-1">{content.submessage}</p>}
        </div>

        {content.isLoading && (
          <div className="flex gap-1 mt-4">
            {[0, 1, 2].map((i) => (
              <motion.div
                key={i}
                className="w-2 h-2 bg-green-600 rounded-full"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 1, delay: i * 0.1, repeat: Infinity }}
              />
            ))}
          </div>
        )}

        {content.showButton && onStartNewConversation && (
          <Button
            onClick={onStartNewConversation}
            className="mt-6 bg-green-600 hover:bg-green-700 text-white font-semibold px-6 py-2 rounded-lg"
          >
            {content.buttonText || '🔄 Start New Conversation'}
          </Button>
        )}
      </motion.div>
    </AnimatePresence>
  );
}
