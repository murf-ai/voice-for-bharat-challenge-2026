'use client';

import { Button } from '@/components/ui/button';

interface TabSwitcherProps {
  activeTab: 'voice' | 'analytics';
  setActiveTab: (tab: 'voice' | 'analytics') => void;
}

export function TabSwitcher({ activeTab, setActiveTab }: TabSwitcherProps) {
  return (
    <div className="flex gap-2">
      <Button
        variant={activeTab === 'voice' ? 'default' : 'outline'}
        size="sm"
        onClick={() => setActiveTab('voice')}
        className={activeTab === 'voice' ? 'bg-green-600 hover:bg-green-700 text-white' : ''}
      >
        Voice Assistant
      </Button>
      <Button
        variant={activeTab === 'analytics' ? 'default' : 'outline'}
        size="sm"
        onClick={() => setActiveTab('analytics')}
        className={activeTab === 'analytics' ? 'bg-green-600 hover:bg-green-700 text-white' : ''}
      >
        Call Analytics
      </Button>
    </div>
  );
}
