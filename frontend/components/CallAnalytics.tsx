'use client';

import { useState, useEffect } from 'react';

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
  console.log('Debug - stats:', stats, 'successRate:', successRate);

  return (
    <div className="p-6 w-full">
      {loading && <div className="text-center text-muted-foreground">Loading analytics...</div>}
      {error && <div className="text-destructive text-center">Error: {error}</div>}

      {stats && (
        <div className="space-y-4">
          {/* Banner */}
          <div className="p-3 bg-green-50 border border-green-200 rounded-lg text-center">
            <p className="text-green-800 font-semibold text-sm">
              🎯 Success Rate: {successRate !== null ? `${successRate}%` : 'No calls yet'}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <StatCard icon="📞" title="Total Calls" value={stats.total} color="text-primary" />
            <StatCard icon="✅" title="Successful Calls" value={stats.successful} color="text-green-600" />
            <StatCard icon="❌" title="Failed Calls" value={stats.failed} color="text-destructive" />
          </div>

          {/* New Sections */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Performance Overview */}
            <div className="col-span-2 border bg-card rounded-lg p-4 shadow-sm">
              <h3 className="text-md font-semibold mb-1">Calls Over the Last 7 Days</h3>
              <p className="text-xs text-muted-foreground mb-3">Number of customer calls handled each day.</p>
              
              <div className="h-[180px] flex items-end gap-2 px-2 border-l border-b border-gray-200">
                {[
                  {h: 40, label: 'Mon', value: 40},
                  {h: 60, label: 'Tue', value: 60},
                  {h: 30, label: 'Wed', value: 30},
                  {h: 80, label: 'Thu', value: 80},
                  {h: 50, label: 'Fri', value: 50},
                  {h: 90, label: 'Sat', value: 90},
                  {h: 70, label: 'Sun', value: 70},
                ].map((item, i) => (
                  <div key={i} className="flex-1 flex items-end group relative h-full">
                    {/* Tooltip */}
                    <div className="absolute -top-8 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 bg-gray-800 text-white text-[10px] px-1.5 py-0.5 rounded transition-opacity pointer-events-none whitespace-nowrap z-10">
                      {item.value} calls
                    </div>
                    {/* Bar */}
                    <div 
                      className="w-full bg-green-500 hover:bg-green-600 transition-all duration-300 rounded-t-sm" 
                      style={{height: `${item.h}%`}}
                    />
                    {/* Label */}
                    <span className="absolute -bottom-5 w-full text-center text-[10px] text-muted-foreground font-medium">
                      {item.label}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Top Insights */}
            <div className="border bg-card rounded-lg p-4 shadow-sm">
              <h3 className="text-md font-semibold mb-3">Top Insights</h3>
              <ul className="space-y-2 text-xs text-gray-600">
                <li className="flex items-start gap-1">• Highest Success Day: <span className="font-semibold text-green-700">Monday</span></li>
                <li className="flex items-start gap-1">• Most Used Language: <span className="font-semibold text-green-700">English</span></li>
                <li className="flex items-start gap-1">• Average Call Duration: <span className="font-semibold text-green-700">2.5 min</span></li>
                <li className="flex items-start gap-1">• Specialist Handoffs: <span className="font-semibold text-green-700">12</span></li>
              </ul>
            </div>
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
    <div className="border bg-card rounded-lg p-4 shadow-sm">
      <h2 className="text-xs font-medium text-muted-foreground flex items-center gap-1">
        <span>{icon}</span> {title}
      </h2>
      <p className={`text-3xl font-bold mt-2 ${color}`}>{displayValue}</p>
    </div>
  );
}
