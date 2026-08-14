'use client';

interface AgentTabsProps {
  currentAgent: 'main' | 'returns_specialist';
}

const AGENTS = [
  { key: 'main', label: 'Main assistant' },
  { key: 'returns_specialist', label: 'Returns specialist' },
] as const;

export function AgentTabs({ currentAgent }: AgentTabsProps) {
  return (
    <div className="fixed top-20 left-6 z-40 flex flex-col gap-2 rounded-lg border bg-background/80 p-4 shadow-sm backdrop-blur-sm">
      <span className="mb-1 text-xs font-medium text-muted-foreground">Active agent</span>
      {AGENTS.map((agent) => {
        const isActive = agent.key === currentAgent;
        return (
          <div
            key={agent.key}
            className="rounded-md border px-3 py-2 text-sm font-medium transition-none"
            style={
              isActive
                ? {
                    borderColor: 'var(--agent-accent)',
                    color: 'var(--agent-accent)',
                    backgroundColor: 'color-mix(in srgb, var(--agent-accent) 12%, white)',
                  }
                : { color: 'var(--muted-foreground)' }
            }
          >
            {agent.label}
          </div>
        );
      })}
    </div>
  );
}
