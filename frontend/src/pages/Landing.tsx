import React from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Sparkles, Network, ArrowRight, GitBranch, Feather } from 'lucide-react';

const BoldPurple = (text: string) => {
  return <span className="bg-gradient-to-r from-loreboard-600 to-loreboard-500 bg-clip-text text-transparent">
        {text}
      </span>
};

const Landing: React.FC = () => {
  return (
    <div className="min-h-screen bg-white">
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
              <Link to="/editor" className="inline-block bg-loreboard-500 hover:bg-loreboard-600 text-white px-6 py-2 rounded-lg transition-colors duration-200 shadow-md hover:shadow-purple-glow font-medium">
                Start Now
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-white pb-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32">
          <div className="text-center">
            {/* Large Hero Icon */}
            <div className="mb-8 flex justify-center">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-br from-loreboard-500 to-loreboard-600 rounded-3xl transform rotate-6 blur-xl opacity-30"></div>
                <div className="relative bg-gradient-to-br from-loreboard-500 to-loreboard-600 p-8 rounded-3xl transform -rotate-3 shadow-2xl">
                  <Feather className="w-24 h-24 text-white" strokeWidth={1.5} />
                </div>
              </div>
            </div>
            
            <h2 className="text-3xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
              Write {BoldPurple('Smarter')}, Write {BoldPurple('Harder')}, Write with {BoldPurple('LoreBoard')}
              
            </h2>
            <p className="text-xl text-gray-700 mb-8 max-w-4xl mx-auto">
              <br/>
              Time to ditch Google Docs, Microsoft Word, and SudoWrite.
             <br/>
             <br/>

              {BoldPurple('LoreBoard')} doesn't let AI hijack the writing process, but doesn't ignore AI either. {BoldPurple('LoreBoard')} utilizes 
              AI models and intuitive design to help you foster the creative process by ensuring consistency, cohesion, and vibrance across your writing.

              <br/>



            </p>
          </div>
        </div>
        
        {/* Decorative elements */}
        <div className="absolute top-1/2 left-0 w-72 h-72 bg-loreboard-200 rounded-full filter blur-3xl opacity-20 -translate-y-1/2 -translate-x-1/2"></div>
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-loreboard-300 rounded-full filter blur-3xl opacity-20 translate-y-1/2 translate-x-1/2"></div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h3 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
              Unleash Your Creative Potential
            </h3>
            <p className="text-lg text-gray-700 max-w-2xl mx-auto">
              Experience the future of storytelling with our comprehensive suite of world-building tools
            </p>
          </div>

          <div className="max-w-6xl mx-auto space-y-16">
            {/* Feature 1 */}
            <div className="flex items-start gap-16 group p-8 rounded-2xl bg-gradient-to-r from-loreboard-50 to-transparent hover:from-loreboard-100/80 hover:to-loreboard-50/50 transition-all duration-300">
              <div className="relative flex-shrink-0">
                <div className="absolute inset-0 bg-gradient-to-br from-loreboard-500 to-loreboard-600 rounded-3xl transform rotate-6 blur-2xl opacity-20 group-hover:opacity-30 transition-opacity duration-300"></div>
                <div className="relative bg-gradient-to-br from-loreboard-500 to-loreboard-600 p-10 rounded-3xl transform -rotate-6 shadow-xl group-hover:shadow-2xl group-hover:-rotate-3 transition-all duration-300">
                  <BookOpen className="w-20 h-20 text-white" strokeWidth={1.5} />
                </div>
              </div>
              <div className="flex-1">
                <h4 className="text-3xl font-bold text-gray-900 mb-4">
                  Dynamic Entity Management
                </h4>
                <p className="text-lg text-gray-700 leading-relaxed">

                  <span className="font-bold"> "Wait, what does he look like again?"</span> <br/><br/>

                  Instead of 'ctrl + f'ing to success, take advantage of {" "}{BoldPurple('LoreBoard')}{"'s "} dynamic entity management. 
                  <br/>
                  Mark characters, locations, and items as entities with a single click, and Loreboard will keep track of them for you.
                  It won't just track text by the entity, but also the attributes the text is about.  <br/> <br/>
                  A side characters appearance? Done. <br/>
                  The wise mentor's dialogue? Done. <br/>
                  Every time the protaganist interacts with the antagonist? Done. <br/>
                  The magical forest's physical description? Done. <br/>
                  The special abilities and drawbacks of that magic item? Done. <br/> <br/>


                  
                  Create and organize profiles for characters, locations, and items. 
                  Our intelligent system maintains relationships and continuity across your entire narrative universe.
                  If you need to find where you described a character's face, or where you first introduced a magic item,{" "}
                   {BoldPurple('LoreBoard')} has you covered. 
                </p>
              </div>
            </div>

            {/* Feature 2 */}
            <div className="flex items-start gap-16 group p-8 rounded-2xl bg-gradient-to-r from-loreboard-50 to-transparent hover:from-loreboard-100/80 hover:to-loreboard-50/50 transition-all duration-300">
              <div className="relative flex-shrink-0">
                <div className="absolute inset-0 bg-gradient-to-br from-loreboard-500 to-loreboard-600 rounded-3xl transform rotate-6 blur-2xl opacity-20 group-hover:opacity-30 transition-opacity duration-300"></div>
                <div className="relative bg-gradient-to-br from-loreboard-500 to-loreboard-600 p-10 rounded-3xl transform -rotate-6 shadow-xl group-hover:shadow-2xl group-hover:-rotate-3 transition-all duration-300">
                  <Sparkles className="w-20 h-20 text-white" strokeWidth={1.5} />
                </div>
              </div>
              <div className="flex-1">
                <h4 className="text-3xl font-bold text-gray-900 mb-4">
                  AI-Powered Auto-Fill and Reword
                </h4>
                <p className="text-lg text-gray-700 leading-relaxed">
                  <span className="font-bold"> Don't stop writing because you can't think of a word thats ____ enough, keep going and let us fill in the blanks.</span> <br/><br/>

                  Need a word thats more ____? <br/>
                  {BoldPurple('LoreBoard')} uses Large Language Models and Vector Embeddings to currate the perfect word for you- if you want us to.
                  Simply throw down some underscores and let the creative juices flow while we handle the speed bumps.
                  As you write more, we'll have a better idea of what you're looking for and we'll be able to make better suggestions.
                  Or, right click a word and just write adjectives- we'll use vectore embeddings to find the best words that accomodates what your looking for.
                </p>
              </div>
            </div>

            {/* Feature 3 */}
            {/* <div className="flex items-start gap-16 group p-8 rounded-2xl bg-gradient-to-r from-loreboard-50 to-transparent hover:from-loreboard-100/80 hover:to-loreboard-50/50 transition-all duration-300">
              <div className="relative flex-shrink-0">
                <div className="absolute inset-0 bg-gradient-to-br from-loreboard-500 to-loreboard-600 rounded-3xl transform rotate-6 blur-2xl opacity-20 group-hover:opacity-30 transition-opacity duration-300"></div>
                <div className="relative bg-gradient-to-br from-loreboard-500 to-loreboard-600 p-10 rounded-3xl transform -rotate-6 shadow-xl group-hover:shadow-2xl group-hover:-rotate-3 transition-all duration-300">
                  <Network className="w-20 h-20 text-white" strokeWidth={1.5} />
                </div>
              </div>
              <div className="flex-1">
                <h4 className="text-3xl font-bold text-gray-900 mb-4">
                  Note Web
                </h4>
                <p className="text-lg text-gray-700 leading-relaxed">
                  <span className="font-bold">Every story deserves its own wiki.</span> <br/><br/>

                  Instead of waiting for your story to have a community that makes one for you, create your own with 
                  {" "}{BoldPurple('LoreBoard')}{"'s "} Note Web.

                  
                  Visualize and manage complex relationships between entities in your world. 
                  Track connections, conflicts, worldbuilding, and lore to ensure narrative coherence and immersive depth.
                  Characters, factions, events, maps, and more.
                  Make sure you and your readers have all the information they need to understand your world.
                  <br/><br/>
                  Build the pages yourself or let us do it for you. Better yet, do both- you can do the fun stuff and let fill the page for that
                  character that appeared in twice in the last ten chapters.
                </p>
              </div>
            </div> */}

            {/* Feature 4 - Version Control */}
            {/* <div className="flex items-start gap-16 group p-8 rounded-2xl bg-gradient-to-r from-loreboard-50 to-transparent hover:from-loreboard-100/80 hover:to-loreboard-50/50 transition-all duration-300">
              <div className="relative flex-shrink-0">
                <div className="absolute inset-0 bg-gradient-to-br from-loreboard-500 to-loreboard-600 rounded-3xl transform rotate-6 blur-2xl opacity-20 group-hover:opacity-30 transition-opacity duration-300"></div>
                <div className="relative bg-gradient-to-br from-loreboard-500 to-loreboard-600 p-10 rounded-3xl transform -rotate-6 shadow-xl group-hover:shadow-2xl group-hover:-rotate-3 transition-all duration-300">
                  <GitBranch className="w-20 h-20 text-white" strokeWidth={1.5} />
                </div>
              </div>
              <div className="flex-1">
                <h4 className="text-3xl font-bold text-gray-900 mb-4">
                  Intelligent Version Control
                </h4>
                <p className="text-lg text-gray-700 leading-relaxed">
                  <span className="font-bold">Seperate the slop from your polished work, and merge them with precision.</span> <br/><br/>
                  
                  Track every revision and explore alternate storylines with confidence. 
                  Feel free to expirement without needing to hit the reset button.
                  Branch your narrative, compare versions, and seamlessly merge changes while preserving your creative history with 
                  {" "}{BoldPurple('LoreBoard')}{"'s "} intelligent version control.
                </p>
              </div>
            </div> */}

          </div>
        </div>

      </section>

      {/* About Section */}
      <section id="about" className="py-20 bg-gradient-to-b from-white to-loreboard-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center">
            <h3 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-6">
              Built for Storytellers, by Storytellers
            </h3>
            <p className="text-lg text-gray-700 mb-8">
              { BoldPurple('LoreBoard')} {' '} revolutionizes the creative writing process by combining intuitive design with cutting-edge AI technology. 
              Whether you're crafting an epic fantasy saga, developing a science fiction universe, or writing contemporary fiction, 
              our platform adapts to your unique creative process.
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
