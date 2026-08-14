import { Button } from '@/components/ui/button';
import { Mic, ShoppingBag, Globe, ArrowRight, BarChart3 } from 'lucide-react';

function WelcomeImage() {
  return (
    <div className="flex items-center justify-center mb-6">
      <Mic size={64} className="text-green-600" strokeWidth={1.5} />
    </div>
  );
}

const FeatureCard = ({ icon: Icon, title, description }: { icon: any, title: string, description: string }) => (
  <div className="bg-white/70 backdrop-blur-sm border border-green-100 p-6 rounded-xl shadow-sm hover:border-green-300 transition-all">
    <div className="mb-4 text-green-600">
      <Icon size={32} strokeWidth={1.5} />
    </div>
    <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
    <p className="text-sm text-gray-600">{description}</p>
  </div>
);

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
      className="relative min-h-screen bg-gray-50 flex flex-col items-center px-4 pt-12 pb-20"
    >
      {/* Background Decor */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 left-0 w-96 h-96 bg-green-200/30 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-emerald-200/30 rounded-full blur-3xl" />
      </div>

      <section className="flex flex-col items-center justify-center text-center max-w-2xl w-full z-10 mb-10">
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
        <p className="text-base md:text-lg text-gray-600 max-w-md mb-6">
          Discover local products, compare options, and connect with nearby businesses using simple voice conversations.
        </p>

        {/* Ready State Message */}
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg w-full">
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
        <div className="mt-8 pt-4 border-t border-gray-200 w-full">
          <p className="text-sm text-gray-500">
            🌐 Supports: English • Telugu • Hindi
          </p>
        </div>
      </section>

      {/* Feature Cards */}
      <section className="max-w-5xl w-full z-10">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <FeatureCard icon={ShoppingBag} title="Local Products" description="Discover nearby products and businesses using natural voice conversations." />
          <FeatureCard icon={Globe} title="Multilingual Support" description="Talk naturally in English, Telugu and Hindi for a seamless shopping experience." />
          <FeatureCard icon={ArrowRight} title="Smart Specialist Handoffs" description="Automatically connects customers to the right specialist whenever additional help is needed." />
          <FeatureCard icon={BarChart3} title="Live Call Analytics" description="Track conversations, customer interactions and agent performance in real time." />
        </div>
      </section>
    </div>
  );
};
