import { Button } from '@/components/ui/button';
import { Mic } from 'lucide-react';

function WelcomeImage() {
  return (
    <div className="flex items-center justify-center mb-6">
      <Mic size={64} className="text-green-600" strokeWidth={1.5} />
    </div>
  );
}

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  return (
    <div
      ref={ref}
      className="bg-white min-h-screen flex flex-col items-center justify-center px-4 py-8"
    >
      <section className="flex flex-col items-center justify-center text-center max-w-2xl w-full">
        {/* Logo Icon */}
        <WelcomeImage />

        {/* Main Title */}
        <h1 className="text-5xl md:text-6xl font-bold text-green-700 mb-2">
          🛍️ VyapaarMitra
        </h1>

        {/* Subtitle */}
        <p className="text-xl md:text-2xl text-gray-800 font-semibold mb-4">
          Your AI Assistant for Local Commerce
        </p>

        {/* Description */}
        <p className="text-base md:text-lg text-gray-600 max-w-md mb-8">
          Discover local products, compare options, and connect with nearby businesses using simple voice conversations.
        </p>

        {/* Ready State Message */}
        <div className="mb-8 p-4 bg-green-50 border border-green-200 rounded-lg w-full">
          <p className="text-green-800 font-medium">
            Ready to start your voice shopping experience.
          </p>
        </div>

        {/* Start Button */}
        <Button
          size="lg"
          onClick={onStartCall}
          className="px-8 py-6 text-lg rounded-full bg-green-600 hover:bg-green-700 text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-200 w-full sm:w-auto"
        >
          🎤 Start Voice Conversation
        </Button>

        {/* Language Support Footer */}
        <div className="mt-12 pt-8 border-t border-gray-200 w-full">
          <p className="text-sm text-gray-500">
            🌐 Supports: English • Telugu • Hindi
          </p>
        </div>
      </section>
    </div>
  );
};
