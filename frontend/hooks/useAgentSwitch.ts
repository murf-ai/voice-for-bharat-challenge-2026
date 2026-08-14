import { useEffect, useState } from 'react';
import { useRoomContext } from '@livekit/components-react';
import { RoomEvent } from 'livekit-client';

export function useAgentSwitch() {
  const room = useRoomContext();
  const [currentAgent, setCurrentAgent] = useState<'main' | 'returns_specialist'>('main');
  const [timeline, setTimeline] = useState<Array<{ agentLabel: string; timestamp: string }>>([]);

  useEffect(() => {
    const handleData = (payload: Uint8Array, participant?: any) => {
      const decoder = new TextDecoder();
      try {
        const data = JSON.parse(decoder.decode(payload));
        if (data.type === 'agent_switch') {
          setCurrentAgent(data.agent === 'returns_specialist' ? 'returns_specialist' : 'main');
          setTimeline(prev => [...prev, { agentLabel: data.label, timestamp: new Date().toLocaleTimeString() }]);
        }
      } catch (e) {
        console.error('Failed to parse agent switch data:', e);
      }
    };
    room.on(RoomEvent.DataReceived, handleData);
    return () => { room.off(RoomEvent.DataReceived, handleData); };
  }, [room]);

  useEffect(() => {
    const handleDisconnect = () => {
      setCurrentAgent('main');
      setTimeline([]);
    };
    room.on(RoomEvent.Disconnected, handleDisconnect);
    return () => { room.off(RoomEvent.Disconnected, handleDisconnect); };
  }, [room]);

  return { currentAgent, timeline };
}
