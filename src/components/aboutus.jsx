import React, { useState, useEffect } from 'react';
import { Heart, Zap, Users, Brain, Globe, TrendingUp, Award, Sparkles, ChevronDown } from 'lucide-react';

export default function AboutUs() {
  const [activeAgent, setActiveAgent] = useState(0);
  const [hoveredVibe, setHoveredVibe] = useState(null);
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const agents = [
    {
      name: "Emotional Intelligence",
      icon: <Heart className="w-8 h-8" />,
      color: "from-pink-500 to-rose-500",
      description: "Analyzes your travel vibes and emotional preferences to create perfectly matched experiences"
    },
    {
      name: "Flight Search",
      icon: <Globe className="w-8 h-8" />,
      color: "from-blue-500 to-cyan-500",
      description: "Finds optimal flight options with real-time pricing and intelligent route optimization"
    },
    {
      name: "Hotel Intelligence",
      icon: <Award className="w-8 h-8" />,
      color: "from-purple-500 to-indigo-500",
      description: "Recommends vibe-matched accommodations that align with your travel personality"
    },
    {
      name: "Transportation",
      icon: <Zap className="w-8 h-8" />,
      color: "from-yellow-500 to-orange-500",
      description: "Plans seamless local travel with optimized routes and cost-effective options"
    },
    {
      name: "Cost Estimation",
      icon: <TrendingUp className="w-8 h-8" />,
      color: "from-green-500 to-emerald-500",
      description: "Provides comprehensive budget analysis with smart optimization suggestions"
    },
    {
      name: "Recommendation",
      icon: <Sparkles className="w-8 h-8" />,
      color: "from-violet-500 to-purple-500",
      description: "Creates personalized day-by-day itineraries tailored to your unique vibe"
    }
  ];

  const vibes = [
    { emoji: "💕", name: "Romantic", color: "bg-pink-100 hover:bg-pink-200" },
    { emoji: "🏔️", name: "Adventure", color: "bg-orange-100 hover:bg-orange-200" },
    { emoji: "🏖️", name: "Beach", color: "bg-blue-100 hover:bg-blue-200" },
    { emoji: "🌲", name: "Nature", color: "bg-green-100 hover:bg-green-200" },
    { emoji: "🏛️", name: "Cultural", color: "bg-purple-100 hover:bg-purple-200" },
    { emoji: "🍽️", name: "Culinary", color: "bg-yellow-100 hover:bg-yellow-200" },
    { emoji: "🧘", name: "Wellness", color: "bg-teal-100 hover:bg-teal-200" }
  ];

  const stats = [
    { value: "6", label: "AI Agents", icon: <Brain className="w-6 h-6" /> },
    { value: "7", label: "Travel Vibes", icon: <Heart className="w-6 h-6" /> },
    { value: "∞", label: "Destinations", icon: <Globe className="w-6 h-6" /> },
    { value: "24/7", label: "Planning", icon: <Zap className="w-6 h-6" /> }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div 
          className="absolute inset-0 opacity-30"
          style={{
            backgroundImage: `radial-gradient(circle at ${scrollY % 100}% ${(scrollY * 0.5) % 100}%, rgba(99, 102, 241, 0.3), transparent 50%)`,
          }}
        />
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16 relative">
          <div className="text-center space-y-6 animate-fade-in">
            <div className="inline-block">
              <span className="inline-flex items-center gap-2 px-4 py-2 bg-white/80 backdrop-blur-sm rounded-full text-sm font-medium text-indigo-600 shadow-lg">
                <Sparkles className="w-4 h-4" />
                AI-Powered Travel Intelligence
              </span>
            </div>
            
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent leading-tight">
              The Future of Travel Planning
            </h1>
            
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Harnessing the power of multi-agent AI systems to create personalized travel experiences 
              that match your emotional vibe and optimize every aspect of your journey.
            </p>

            <div className="animate-bounce mt-8">
              <ChevronDown className="w-8 h-8 mx-auto text-indigo-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, idx) => (
            <div 
              key={idx}
              className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-1 cursor-pointer"
            >
              <div className="flex items-center justify-center mb-3 text-indigo-600">
                {stat.icon}
              </div>
              <div className="text-4xl font-bold text-gray-900 text-center mb-2">
                {stat.value}
              </div>
              <div className="text-sm text-gray-600 text-center font-medium">
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Mission Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="bg-white rounded-3xl shadow-2xl p-8 sm:p-12 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-purple-200 to-pink-200 rounded-full blur-3xl opacity-50 -mr-32 -mt-32" />
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-gradient-to-br from-blue-200 to-indigo-200 rounded-full blur-3xl opacity-50 -ml-32 -mb-32" />
          
          <div className="relative space-y-6">
            <h2 className="text-4xl font-bold text-gray-900 text-center mb-8">
              Our Mission
            </h2>
            <p className="text-lg text-gray-700 leading-relaxed text-center max-w-4xl mx-auto">
              We believe travel should be more than just booking flights and hotels. 
              It should be an <span className="font-semibold text-indigo-600">emotionally intelligent experience</span> that 
              understands your unique vibe, preferences, and dreams. Our multi-agent AI system works 
              tirelessly to ensure every aspect of your journey is perfectly orchestrated, 
              from finding the ideal flight to crafting day-by-day adventures that resonate with your soul.
            </p>
          </div>
        </div>
      </div>

      {/* AI Agents Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-4xl font-bold text-gray-900 text-center mb-4">
          Meet Our AI Agents
        </h2>
        <p className="text-lg text-gray-600 text-center mb-12 max-w-2xl mx-auto">
          Six specialized AI agents working in harmony to create your perfect journey
        </p>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {agents.map((agent, idx) => (
            <div
              key={idx}
              onMouseEnter={() => setActiveAgent(idx)}
              className={`bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl transition-all duration-300 cursor-pointer ${
                activeAgent === idx ? 'ring-4 ring-indigo-500 -translate-y-2' : ''
              }`}
            >
              <div className={`inline-flex p-4 rounded-xl bg-gradient-to-br ${agent.color} text-white mb-4`}>
                {agent.icon}
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                {agent.name}
              </h3>
              <p className="text-gray-600 leading-relaxed">
                {agent.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Travel Vibes Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-4xl font-bold text-gray-900 text-center mb-4">
          Discover Your Travel Vibe
        </h2>
        <p className="text-lg text-gray-600 text-center mb-12 max-w-2xl mx-auto">
          Our emotional intelligence system understands 7 distinct travel personalities
        </p>

        <div className="flex flex-wrap justify-center gap-4">
          {vibes.map((vibe, idx) => (
            <div
              key={idx}
              onMouseEnter={() => setHoveredVibe(idx)}
              onMouseLeave={() => setHoveredVibe(null)}
              className={`${vibe.color} rounded-2xl p-6 transition-all duration-300 cursor-pointer ${
                hoveredVibe === idx ? 'scale-110 shadow-2xl' : 'shadow-lg'
              }`}
            >
              <div className="text-5xl mb-2 text-center">{vibe.emoji}</div>
              <div className="text-sm font-semibold text-gray-800 text-center">
                {vibe.name}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Technology Stack */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-3xl p-8 sm:p-12 text-white">
          <h2 className="text-4xl font-bold text-center mb-8">
            Powered by Cutting-Edge Technology
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center space-y-3">
              <div className="inline-flex p-4 bg-white/20 rounded-xl backdrop-blur-sm">
                <Brain className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-bold">Multi-Agent AI</h3>
              <p className="text-indigo-100">
                LangGraph orchestration with specialized AI agents for intelligent decision-making
              </p>
            </div>
            
            <div className="text-center space-y-3">
              <div className="inline-flex p-4 bg-white/20 rounded-xl backdrop-blur-sm">
                <Zap className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-bold">Real-Time Data</h3>
              <p className="text-indigo-100">
                Live flight & hotel data via SERP API with instant price updates and availability
              </p>
            </div>
            
            <div className="text-center space-y-3">
              <div className="inline-flex p-4 bg-white/20 rounded-xl backdrop-blur-sm">
                <Heart className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-bold">Emotional Intelligence</h3>
              <p className="text-indigo-100">
                Vibe-based recommendations powered by advanced AI to match your travel personality
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 mb-16">
        <div className="bg-white rounded-3xl shadow-2xl p-12 text-center relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-pink-500/10" />
          
          <div className="relative space-y-6">
            <h2 className="text-4xl font-bold text-gray-900">
              Ready to Experience the Future?
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Let our AI agents craft your perfect journey with emotional intelligence and real-time optimization.
            </p>
            <button className="inline-flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-8 py-4 rounded-full font-semibold text-lg shadow-xl hover:shadow-2xl hover:scale-105 transition-all duration-300">
              <Sparkles className="w-5 h-5" />
              Start Planning Your Trip
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}// Example usage in parent component
import { useNavigate } from 'react-router-dom'

const ParentComponent = () => {
  const navigate = useNavigate()

  // ...other handlers...

  const handleAboutNavigate = () => {
    navigate('/aboutus')
  }

  return (
    <Header
      // ...other props...
      onAboutNavigate={handleAboutNavigate}
      // ...other props...
    />
    // ...rest of your component...
  )
}