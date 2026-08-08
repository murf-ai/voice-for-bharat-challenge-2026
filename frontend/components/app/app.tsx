'use client';

import { useEffect, useMemo } from 'react';
import { TokenSource } from 'livekit-client';
import { useSession } from '@livekit/components-react';
import { WarningIcon } from '@phosphor-icons/react/dist/ssr';
import { toast } from 'sonner';

import type { AppConfig } from '@/app-config';
import { AgentSessionProvider } from '@/components/agents-ui/agent-session-provider';
import { StartAudioButton } from '@/components/agents-ui/start-audio-button';
import { ViewController } from '@/components/app/view-controller';
import { Toaster } from '@/components/ui/sonner';

import { useAgentErrors } from '@/hooks/useAgentErrors';
import { useDebugMode } from '@/hooks/useDebug';
import { useMicrophonePermission } from '@/hooks/useMicrophonePermission';

import { getSandboxTokenSource } from '@/lib/utils';

const IN_DEVELOPMENT = process.env.NODE_ENV !== 'production';

function AppSetup() {
  useDebugMode({ enabled: IN_DEVELOPMENT });
  useAgentErrors();

  return null;
}

interface AppProps {
  appConfig: AppConfig;
}

export function App({ appConfig }: AppProps) {
  const tokenSource = useMemo(() => {
    return typeof process.env.NEXT_PUBLIC_CONN_DETAILS_ENDPOINT === 'string'
      ? getSandboxTokenSource(appConfig)
      : TokenSource.endpoint('/api/token');
  }, [appConfig]);

  const session = useSession(
    tokenSource,
    appConfig.agentName ? { agentName: appConfig.agentName } : undefined
  );

  const { isDenied } = useMicrophonePermission();

  useEffect(() => {
    if (isDenied) {
      toast.error('🎤 Microphone Permission Required', {
        description:
          "VyapaarMitra cannot hear your voice because microphone access is blocked. Please click the lock icon in your browser's address bar, allow microphone access, and refresh the page.",
        duration: 10000,
      });
    }
  }, [isDenied]);

  return (
    <AgentSessionProvider session={session}>
      <AppSetup />

      <main className="grid h-svh grid-cols-1 place-content-center">
        {isDenied && (
          <div className="mx-auto mb-4 max-w-lg rounded-lg border border-red-300 bg-red-50 p-4 text-center text-red-700">
            <h3 className="font-semibold">
              🎤 Microphone Permission Required
            </h3>

            <p className="mt-2 text-sm">
              VyapaarMitra cannot hear your voice because microphone access is
              blocked. Please click the 🔒 icon in your browser's address bar,
              allow microphone access, and refresh the page.
            </p>
          </div>
        )}

        <ViewController appConfig={appConfig} />
      </main>

      <StartAudioButton label="Start Audio" />

      <Toaster
        icons={{
          warning: <WarningIcon weight="bold" />,
        }}
        position="top-center"
        className="toaster group"
        style={
          {
            '--normal-bg': 'var(--popover)',
            '--normal-text': 'var(--popover-foreground)',
            '--normal-border': 'var(--border)',
          } as React.CSSProperties
        }
      />
    </AgentSessionProvider>
  );
}