import React from 'react';
import { BookOpen, Sparkles, Network, ArrowRight } from 'lucide-react';

const Landing: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-loreboard-50 via-white to-loreboard-100">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-sm border-b border-loreboard-100 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-loreboard-600 to-loreboard-500 bg-clip-text text-transparent">
                LoreBoard
              </h1>
            </div>
            <div className="flex items-center gap-6">
              <a href="#features" className="text-gray-700 hover:text-loreboard-600 px-3 py-2 rounded-md hover:bg-loreboard-50 transition-all duration-200">
                Features
              </a>
              <a href="#about" className="text-gray-700 hover:text-loreboard-600 px-3 py-2 rounded-md hover:bg-loreboard-50 transition-all duration-200">
                About
              </a>
              <button className="bg-loreboard-500 hover:bg-loreboard-600 text-white px-6 py-2 rounded-lg transition-colors duration-200 shadow-md hover:shadow-purple-glow font-medium">
                Start Now
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32">
          <div className="text-center">
            <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
              Craft Your Universe with
              <span className="block bg-gradient-to-r from-loreboard-600 to-loreboard-500 bg-clip-text text-transparent">
                Intelligent Storytelling
              </span>
            </h2>
            <p className="text-xl text-gray-700 mb-8 max-w-3xl mx-auto">
              Transform your creative vision into immersive narratives with LoreBoard's AI-powered world-building platform. 
              Seamlessly manage characters, locations, and storylines while maintaining perfect continuity.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="bg-loreboard-500 hover:bg-loreboard-600 text-white px-8 py-4 rounded-lg transition-colors duration-200 shadow-lg hover:shadow-purple-glow font-semibold text-lg flex items-center justify-center gap-2">
                Start Writing Now
                <ArrowRight className="w-5 h-5" />
              </button>
              <button className="border-2 border-loreboard-500 text-loreboard-600 hover:bg-loreboard-50 px-8 py-4 rounded-lg transition-colors duration-200 font-semibold text-lg">
                View Demo
              </button>
            </div>
          </div>
        </div>
        
        {/* Decorative elements */}
        <div className="absolute top-1/2 left-0 w-72 h-72 bg-loreboard-200 rounded-full filter blur-3xl opacity-20 -translate-y-1/2 -translate-x-1/2"></div>
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-loreboard-300 rounded-full filter blur-3xl opacity-20 translate-y-1/2 translate-x-1/2"></div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h3 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
              Unleash Your Creative Potential
            </h3>
            <p className="text-lg text-gray-700 max-w-2xl mx-auto">
              Experience the future of storytelling with our comprehensive suite of world-building tools
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-white rounded-xl shadow-lg p-8 border border-loreboard-100 hover:shadow-purple-glow transition-shadow duration-300">
              <div className="bg-gradient-to-br from-loreboard-100 to-loreboard-50 w-16 h-16 rounded-lg flex items-center justify-center mb-6">
                <BookOpen className="w-8 h-8 text-loreboard-600" />
              </div>
              <h4 className="text-xl font-semibold text-gray-900 mb-3">
                Dynamic Entity Management
              </h4>
              <p className="text-gray-700">
                Create and organize complex character profiles, intricate locations, and meaningful items. 
                Our intelligent system maintains relationships and continuity across your entire narrative universe.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-white rounded-xl shadow-lg p-8 border border-loreboard-100 hover:shadow-purple-glow transition-shadow duration-300">
              <div className="bg-gradient-to-br from-loreboard-100 to-loreboard-50 w-16 h-16 rounded-lg flex items-center justify-center mb-6">
                <Sparkles className="w-8 h-8 text-loreboard-600" />
              </div>
              <h4 className="text-xl font-semibold text-gray-900 mb-3">
                AI-Powered Auto-Fill
              </h4>
              <p className="text-gray-700">
                Harness the power of advanced language models to generate contextually aware content. 
                Fill narrative gaps, develop dialogue, and expand descriptions while maintaining your unique voice.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-white rounded-xl shadow-lg p-8 border border-loreboard-100 hover:shadow-purple-glow transition-shadow duration-300">
              <div className="bg-gradient-to-br from-loreboard-100 to-loreboard-50 w-16 h-16 rounded-lg flex items-center justify-center mb-6">
                <Network className="w-8 h-8 text-loreboard-600" />
              </div>
              <h4 className="text-xl font-semibold text-gray-900 mb-3">
                Relationship Mapping
              </h4>
              <p className="text-gray-700">
                Visualize and manage complex relationships between entities in your world. 
                Track connections, conflicts, and dependencies to ensure narrative coherence and depth.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-20 bg-gradient-to-b from-white/50 to-loreboard-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center">
            <h3 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-6">
              Built for Storytellers, by Storytellers
            </h3>
            <p className="text-lg text-gray-700 mb-8">
              LoreBoard revolutionizes the creative writing process by combining intuitive design with cutting-edge AI technology. 
              Whether you're crafting an epic fantasy saga, developing a science fiction universe, or writing contemporary fiction, 
              our platform adapts to your unique creative process.
            </p>
            <p className="text-lg text-gray-700 mb-12">
              Join thousands of writers who have discovered the perfect balance between creative freedom and organizational structure. 
              Let LoreBoard handle the complexity while you focus on what matters most: telling extraordinary stories.
            </p>
            <button className="bg-loreboard-500 hover:bg-loreboard-600 text-white px-10 py-4 rounded-lg transition-colors duration-200 shadow-lg hover:shadow-purple-glow font-semibold text-lg flex items-center justify-center gap-2 mx-auto">
              Begin Your Journey
              <ArrowRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-loreboard-950 text-loreboard-300 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-4 md:mb-0">
              <h4 className="text-2xl font-bold text-white mb-2">LoreBoard</h4>
              <p className="text-loreboard-400">Empowering storytellers worldwide</p>
            </div>
            <div className="flex gap-6">
              <a href="#" className="hover:text-white transition-colors duration-200">Privacy Policy</a>
              <a href="#" className="hover:text-white transition-colors duration-200">Terms of Service</a>
              <a href="#" className="hover:text-white transition-colors duration-200">Contact</a>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-loreboard-800 text-center text-loreboard-400">
            <p>&copy; 2025 LoreBoard. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
