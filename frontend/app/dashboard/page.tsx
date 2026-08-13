'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { CallAnalytics } from '@/components/CallAnalytics';

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-background text-foreground font-sans">
      {/* Header */}
      <header className="border-b p-4 flex items-center justify-between">
        <div className="text-xl font-bold">VyapaarMitra</div>
        <div className="text-xs text-muted-foreground">BUILT WITH LIVEKIT AGENTS</div>
      </header>

      <main>
        <CallAnalytics />
        <div className="mt-12 px-8">
            <Link href="/" passHref>
                <Button variant="outline">Back to Home</Button>
            </Link>
        </div>
      </main>
    </div>
  );
}
