'use client';

import { motion, AnimatePresence } from 'motion/react';
import type { AgentState } from '@livekit/components-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/shadcn/utils';

interface AgentStatusCardProps {
  state?: AgentState;
  onStartNewConversation?: () => void;
  className?: string;
}

export function AgentStatusCard({
  state,
  onStartNewConversation,
  className,
}: AgentStatusCardProps) {
  const getStatusContent = () => {
    switch (state) {
      case 'disconnected':
        return {
          emoji: '🟢',
          title: 'Ready',
          description: 'Ready to start your voice shopping experience.',
          subtitle: null,
          showButton: false,
          isLoading: false,
          bgColor: 'bg-green-50 dark:bg-green-950/20',
          borderColor: 'border-green-200 dark:border-green-800',
          textColor: 'text-green-900 dark:text-green-100',
          subtitleColor: 'text-green-700 dark:text-green-200',
        };

      case 'connecting':
      case 'initializing':
        return {
          emoji: '🟡',
          title: 'Connecting',
          description: 'Connecting...',
          subtitle: 'Joining VyapaarMitra. Please wait.',
          showButton: false,
          isLoading: true,
          bgColor: 'bg-yellow-50 dark:bg-yellow-950/20',
          borderColor: 'border-yellow-200 dark:border-yellow-800',
          textColor: 'text-yellow-900 dark:text-yellow-100',
          subtitleColor: 'text-yellow-700 dark:text-yellow-200',
        };

      case 'listening':
        return {
          emoji: '🎤',
          title: 'Listening',
          description: 'Listening...',
          subtitle: 'Listening to you.',
          showButton: false,
          isLoading: false,
          bgColor: 'bg-blue-50 dark:bg-blue-950/20',
          borderColor: 'border-blue-200 dark:border-blue-800',
          textColor: 'text-blue-900 dark:text-blue-100',
          subtitleColor: 'text-blue-700 dark:text-blue-200',
        };

      case 'thinking':
        return {
          emoji: '🔊',
          title: 'Speaking',
          description: 'Speaking...',
          subtitle: 'VyapaarMitra is responding.',
          showButton: false,
          isLoading: false,
          bgColor: 'bg-purple-50 dark:bg-purple-950/20',
          borderColor: 'border-purple-200 dark:border-purple-800',
          textColor: 'text-purple-900 dark:text-purple-100',
          subtitleColor: 'text-purple-700 dark:text-purple-200',
        };

      case 'speaking':
        return {
          emoji: '🔊',
          title: 'Speaking',
          description: 'Speaking...',
          subtitle: 'VyapaarMitra is responding.',
          showButton: false,
          isLoading: false,
          bgColor: 'bg-purple-50 dark:bg-purple-950/20',
          borderColor: 'border-purple-200 dark:border-purple-800',
          textColor: 'text-purple-900 dark:text-purple-100',
          subtitleColor: 'text-purple-700 dark:text-purple-200',
        };

      case 'failed':
        return {
          emoji: '🔴',
          title: 'Call Ended',
          description: 'Thank you for using VyapaarMitra.',
          subtitle: null,
          showButton: true,
          isLoading: false,
          bgColor: 'bg-red-50 dark:bg-red-950/20',
          borderColor: 'border-red-200 dark:border-red-800',
          textColor: 'text-red-900 dark:text-red-100',
          subtitleColor: 'text-red-700 dark:text-red-200',
        };

      default:
        return {
          emoji: '🟢',
          title: 'Ready',
          description: 'Ready to start your voice shopping experience.',
          subtitle: null,
          showButton: false,
          isLoading: false,
          bgColor: 'bg-green-50 dark:bg-green-950/20',
          borderColor: 'border-green-200 dark:border-green-800',
          textColor: 'text-green-900 dark:text-green-100',
          subtitleColor: 'text-green-700 dark:text-green-200',
        };
    }
  };

  const content = getStatusContent();

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={`status-${state}`}
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -6 }}
        transition={{ duration: 0.2 }}
        className={cn(
          'inline-flex max-w-full items-center gap-2 rounded-full border px-3 py-1.5 text-sm shadow-sm backdrop-blur-sm',
          content.bgColor,
          content.borderColor,
          content.textColor,
          className
        )}
      >
        <div className="relative flex items-center justify-center">
          <span className="text-base leading-none">{content.emoji}</span>
          {content.isLoading && (
            <motion.span
              animate={{ rotate: 360 }}
              transition={{ duration: 1.2, repeat: Infinity, ease: 'linear' }}
              className="absolute inset-0 flex items-center justify-center"
            >
              <span className="text-[10px] leading-none">⟳</span>
            </motion.span>
          )}
        </div>
        <span className="whitespace-nowrap font-medium leading-none">{content.title}</span>
        {content.showButton && onStartNewConversation && (
          <Button
            onClick={onStartNewConversation}
            variant="default"
            className="ml-1 h-6 rounded-full bg-green-600 px-2.5 text-[11px] font-semibold text-white hover:bg-green-700 dark:bg-green-700 dark:hover:bg-green-600"
          >
            Start Again
          </Button>
        )}
      </motion.div>
    </AnimatePresence>
  );
}
