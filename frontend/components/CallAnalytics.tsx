'use client';

import { useState, useEffect, useRef } from 'react';

export function CallAnalytics() {
  const [stats, setStats] = useState<{ total: number; successful: number; failed: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/call-stats')
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch stats');
        return res.json();
      })
      .then((data) => {
        console.log('API Response:', data);
        setStats({
          total: data.total_calls,
          successful: data.successful_calls,
          failed: data.failed_calls,
        });
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const successRate = stats && stats.total > 0 ? Math.round((stats.successful / stats.total) * 100) : null;

  return (
    <div className="p-8 max-w-5xl mx-auto">
      {loading && <div className="text-center text-muted-foreground">Loading analytics...</div>}
      {error && <div className="text-destructive text-center">Error: {error}</div>}

      {stats && (
        <div className="space-y-6">
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg text-center">
            <p className="text-green-800 font-medium">
              🎯 Success Rate: {successRate !== null ? `${successRate}%` : 'No calls yet'}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <StatCard icon="📞" title="Total Calls" value={stats.total} color="text-primary" />
            <StatCard icon="✅" title="Successful Calls" value={stats.successful} color="text-green-600" />
            <StatCard icon="❌" title="Failed Calls" value={stats.failed} color="text-destructive" />
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ icon, title, value, color }: { icon: string; title: string; value: number; color: string }) {
  const [displayValue, setDisplayValue] = useState(0);
  const duration = 800; // ms

  useEffect(() => {
    let startTime: number | null = null;
    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = timestamp - startTime;
      const percentage = Math.min(progress / duration, 1);
      setDisplayValue(Math.floor(percentage * value));
      if (progress < duration) requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);
  }, [value]);

  return (
    <div className="border bg-card rounded-lg p-6 shadow-sm hover:scale-105 transition-transform duration-200">
      <h2 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
        <span>{icon}</span> {title}
      </h2>
      <p className={`text-5xl font-bold mt-4 ${color}`}>{displayValue}</p>
    </div>
  );
}
