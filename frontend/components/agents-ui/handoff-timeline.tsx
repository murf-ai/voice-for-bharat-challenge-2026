export function HandoffTimeline({ timeline }: { timeline: Array<{ agentLabel: string; timestamp: string }> }) {
  if (timeline.length === 0) return null;
  return (
    <div className="fixed top-20 right-6 z-40 max-w-sm rounded-lg border bg-background/80 p-4 shadow-sm backdrop-blur-sm">
      <h3 className="mb-2 text-sm font-bold">Handoff Timeline</h3>
      <div className="flex flex-col gap-1">
        {timeline.map((entry, i) => (
          <div
            key={i}
            className="border-l-2 pl-2 text-xs text-muted-foreground"
            style={{ borderColor: 'var(--agent-accent)' }}
          >
            {entry.agentLabel} -- connected {entry.timestamp}
          </div>
        ))}
      </div>
    </div>
  );
}
