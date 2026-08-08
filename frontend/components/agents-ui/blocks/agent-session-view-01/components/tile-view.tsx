import React, { useMemo } from 'react';
import { Track } from 'livekit-client';
import { AnimatePresence, type MotionProps, motion } from 'motion/react';
import {
  type AgentState,
  type TrackReference,
  VideoTrack,
  useLocalParticipant,
  useTracks,
  useVoiceAssistant,
} from '@livekit/components-react';
import { cn } from '@/lib/shadcn/utils';
import { AgentStatusCard } from '@/components/agents-ui/agent-status-card';
import { AudioVisualizer } from './audio-visualizer';

const ANIMATION_TRANSITION: MotionProps['transition'] = {
  type: 'spring',
  stiffness: 675,
  damping: 75,
  mass: 1,
};

export function useLocalTrackRef(source: Track.Source) {
  const { localParticipant } = useLocalParticipant();
  const publication = localParticipant.getTrackPublication(source);
  const trackRef = useMemo<TrackReference | undefined>(
    () => (publication ? { source, participant: localParticipant, publication } : undefined),
    [source, publication, localParticipant]
  );
  return trackRef;
}

interface TileLayoutProps {
  chatOpen: boolean;
  agentState?: AgentState;
  onStartNewConversation?: () => void;
  audioVisualizerType?: 'bar' | 'wave' | 'grid' | 'radial' | 'aura';
  audioVisualizerColor?: `#${string}`;
  audioVisualizerColorShift?: number;
  audioVisualizerWaveLineWidth?: number;
  audioVisualizerGridRowCount?: number;
  audioVisualizerGridColumnCount?: number;
  audioVisualizerRadialBarCount?: number;
  audioVisualizerRadialRadius?: number;
  audioVisualizerBarCount?: number;
}

export function TileLayout({
  chatOpen,
  agentState,
  onStartNewConversation,
  audioVisualizerType,
  audioVisualizerColor,
  audioVisualizerColorShift,
  audioVisualizerBarCount,
  audioVisualizerRadialBarCount,
  audioVisualizerRadialRadius,
  audioVisualizerGridRowCount,
  audioVisualizerGridColumnCount,
  audioVisualizerWaveLineWidth,
}: TileLayoutProps) {
  const { videoTrack: agentVideoTrack } = useVoiceAssistant();
  const [screenShareTrack] = useTracks([Track.Source.ScreenShare]);
  const cameraTrack: TrackReference | undefined = useLocalTrackRef(Track.Source.Camera);

  const isCameraEnabled = cameraTrack && !cameraTrack.publication.isMuted;
  const isScreenShareEnabled = screenShareTrack && !screenShareTrack.publication.isMuted;
  const showSecondaryTiles = isCameraEnabled || isScreenShareEnabled;

  const animationDelay = chatOpen ? 0 : 0.15;
  const isAvatar = agentVideoTrack !== undefined;
  const videoWidth = agentVideoTrack?.publication.dimensions?.width ?? 0;
  const videoHeight = agentVideoTrack?.publication.dimensions?.height ?? 0;

  return (
    <div className="absolute inset-x-0 top-8 bottom-32 z-50 md:top-12 md:bottom-40">
      <div className="relative mx-auto h-full max-w-2xl px-4 md:px-0">
        <div className="flex h-full flex-col gap-3">
          <div className="flex justify-center px-2 md:px-0">
            <AgentStatusCard
              state={agentState}
              onStartNewConversation={onStartNewConversation}
              className="w-fit"
            />
          </div>

          <div className="flex-1 overflow-hidden rounded-[36px] border border-border bg-background/80 shadow-[0_30px_80px_rgba(15,23,42,0.14)]">
            <div className="h-full w-full overflow-hidden bg-slate-950/5 dark:bg-white/5">
              <div className="flex h-full w-full items-center justify-center px-6">
                <AnimatePresence mode="wait">
                  {!isAvatar ? (
                    <motion.div
                      key="audio-visualizer"
                      initial={{ opacity: 0, scale: 0.96 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.96 }}
                      transition={{
                        ...ANIMATION_TRANSITION,
                        delay: animationDelay,
                      }}
                      className="flex h-full w-full items-center justify-center"
                    >
                      <AudioVisualizer
                        audioVisualizerType={audioVisualizerType}
                        audioVisualizerColor={audioVisualizerColor}
                        audioVisualizerColorShift={audioVisualizerColorShift}
                        audioVisualizerBarCount={audioVisualizerBarCount}
                        audioVisualizerRadialBarCount={audioVisualizerRadialBarCount}
                        audioVisualizerRadialRadius={audioVisualizerRadialRadius}
                        audioVisualizerGridRowCount={audioVisualizerGridRowCount}
                        audioVisualizerGridColumnCount={audioVisualizerGridColumnCount}
                        audioVisualizerWaveLineWidth={audioVisualizerWaveLineWidth}
                        isChatOpen={chatOpen}
                        className="mx-auto h-full w-full max-w-[95%] max-h-[95%]"
                      />
                    </motion.div>
                  ) : (
                    <motion.div
                      key="avatar"
                      initial={{ opacity: 0, scale: 0.96 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.96 }}
                      transition={{
                        ...ANIMATION_TRANSITION,
                        delay: animationDelay,
                      }}
                      className="absolute inset-0"
                    >
                      <VideoTrack
                        width={videoWidth}
                        height={videoHeight}
                        trackRef={agentVideoTrack}
                        className="h-full w-full object-cover"
                      />
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </div>

          {showSecondaryTiles && (
            <div className="grid gap-4 md:grid-cols-2">
              {cameraTrack && isCameraEnabled && (
                <div className="overflow-hidden rounded-3xl border border-border bg-background/80 p-2 shadow-lg shadow-black/5">
                  <VideoTrack
                    trackRef={cameraTrack}
                    width={cameraTrack.publication.dimensions?.width ?? 0}
                    height={cameraTrack.publication.dimensions?.height ?? 0}
                    className="h-full w-full rounded-3xl object-cover"
                  />
                </div>
              )}
              {screenShareTrack && isScreenShareEnabled && (
                <div className="overflow-hidden rounded-3xl border border-border bg-background/80 p-2 shadow-lg shadow-black/5">
                  <VideoTrack
                    trackRef={screenShareTrack}
                    width={screenShareTrack.publication.dimensions?.width ?? 0}
                    height={(screenShareTrack.publication.dimensions?.height ?? 0)}
                    className="h-full w-full rounded-3xl object-cover"
                  />
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
