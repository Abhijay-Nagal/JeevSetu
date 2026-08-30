import React, { useRef, useState, useEffect } from "react";
import HTMLFlipBook from "react-pageflip";
import { Link } from "react-router-dom";
import { Leaf, Users, MessageCircle, FileText, Globe, Search, ArrowRight, BookOpen, Camera, Shield } from "lucide-react";
import { api } from "../lib/api";
import ShinyText from "../components/ui/ShinyText";
import SplitText from "../components/ui/SplitText";

export const route = { layout: "app", path: "/", public: true };

const Page = React.forwardRef((props, ref) => {
  return (
    <div 
      className={`page shadow-[inset_0_0_20px_rgba(0,0,0,0.5)] border-r border-black/30 p-6 overflow-hidden relative ${props.imagePage ? 'bg-black' : 'bg-[#0B3D2E] text-[#F8F6E9]'}`} 
      ref={ref}
    >
      {/* Left click zone for previous page */}
      <div 
        className="absolute left-0 top-16 bottom-16 w-1/3 z-20 cursor-pointer" 
        onClick={(e) => { 
          e.stopPropagation(); 
          if (props.bookRef?.current?.pageFlip()) {
             props.bookRef.current.pageFlip().flipPrev();
          }
        }} 
      />
      {/* Right click zone for next page */}
      <div 
        className="absolute right-0 top-16 bottom-16 w-1/3 z-20 cursor-pointer" 
        onClick={(e) => { 
          e.stopPropagation(); 
          if (props.bookRef?.current?.pageFlip()) {
             props.bookRef.current.pageFlip().flipNext();
          }
        }} 
      />

      {props.imagePage ? (
        <div className="absolute inset-0 w-full h-full pointer-events-none">
          <img src={props.imageSrc} alt="Illustration" className="w-full h-full object-cover opacity-90" />
        </div>
      ) : (
        <div className="h-full w-full relative z-30 pointer-events-auto flex flex-col">
          {props.children}
        </div>
      )}
      
      {props.number && !props.imagePage && (
        <div className="absolute bottom-4 right-4 text-xs font-semibold opacity-40 pointer-events-none">
          {props.number}
        </div>
      )}
    </div>
  );
});

export default function HomeFeed() {
  const bookRef = useRef(null);
  const [isMobile, setIsMobile] = useState(typeof window !== "undefined" ? window.innerWidth < 768 : false);

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const next = (e) => { e.preventDefault(); bookRef.current?.pageFlip()?.flipNext(); };

  return (
    <div className="flex flex-col items-center justify-start w-full min-h-[calc(100vh-4rem)] overflow-y-auto pt-1 pb-8">
      <div className="z-10 perspective-1000 w-full max-w-[700px] h-[470px] flex justify-center items-center shrink-0">
        <HTMLFlipBook 
          width={320} 
          height={450} 
          showCover={false}
          className="mx-auto shadow-2xl drop-shadow-2xl book-container"
          ref={bookRef}
          useMouseEvents={true}
          usePortrait={true}
        >
          {[

          <Page bookRef={bookRef}>
            <div className="flex flex-col items-center justify-between h-full p-6 text-center">
              <div className="flex-1 flex items-center justify-center w-full">
                <img src="/jeevsetu-logo.png" alt="JeevSetu" className="w-5/6 max-w-[280px] h-auto brightness-0 invert opacity-80 drop-shadow-lg" />
              </div>
              <div className="mt-auto pt-6 text-[10px] space-y-2 opacity-50 font-medium shrink-0">
                <p>Published by JeevSetu Conservation Initiative</p>
                <p>First Edition, 2026</p>
                <p>© All Rights Reserved</p>
                <p className="pt-4 border-t border-white/20 mt-4 max-w-[200px] mx-auto">
                  Dedicated to the incredible biodiversity of India and those who protect it.
                </p>
              </div>
            </div>
          </Page>,

          /* Page 2 - Cover Title (Welcome to JeevSetu) (Right) */
          <Page bookRef={bookRef}>
            <div className="flex flex-col h-full py-2">
              <img src="/jeevsetu-logo.png" alt="JeevSetu" className="w-20 h-auto mx-auto mb-4 brightness-0 invert shrink-0" />
              <div className="overflow-y-auto no-scrollbar flex-1 flex flex-col w-full text-center">
                <h1 className="text-2xl font-bold mb-4 text-[#F4C430] leading-tight">
                  <SplitText text="Bridging People & Wildlife" />
                </h1>
                <p className="text-sm opacity-90 mb-3 px-2 leading-relaxed">
                  India is home to extraordinary biodiversity from Himalayan forests to coastal wetlands, grasslands, deserts and urban ecosystems.
                </p>
                <p className="text-sm opacity-90 mb-3 px-2 leading-relaxed">
                  But protecting this natural heritage isn't the responsibility of scientists and conservationists alone.
                </p>
                <p className="text-sm font-semibold mb-3 px-2 text-[#F4C430]">
                  JeevSetu connects you to the people, knowledge and opportunities that help protect it.
                </p>
              </div>
              <button 
                onClick={next} 
                className="mt-4 mx-auto flex items-center gap-2 rounded-full bg-[#F4C430] px-6 py-2.5 text-[#0B3D2E] font-bold hover:bg-[#F4C430]/90 transition shadow-lg shrink-0"
              >
                Begin the Journey <ArrowRight size={18} />
              </button>
            </div>
          </Page>,

          /* Page 2 - Left Illustration (BNHS) */
          !isMobile && <Page imagePage={true} imageSrc="/book/bnhs.jpg" bookRef={bookRef} />,

          /* Page 3 - Who is BNHS? */
          <Page number="1" bookRef={bookRef}>
            <div className="flex flex-col h-full">
              <h2 className="text-2xl font-bold mb-4 text-[#F4C430]"><ShinyText text="Meet BNHS" /></h2>
              <div className="overflow-y-auto no-scrollbar flex-1 pb-4">
                <p className="text-sm opacity-90 leading-relaxed mb-4">
                  The Bombay Natural History Society (BNHS) is one of India's oldest organisations dedicated to nature conservation, founded in 1883.
                </p>
                <p className="text-sm opacity-90 leading-relaxed mb-4">
                  For more than a century, BNHS has worked to understand and protect India's biodiversity through scientific research, conservation, education and public awareness.
                </p>
                <div className="bg-white/10 p-4 rounded-xl text-xs space-y-3">
                  <div className="flex gap-2"><b>1883</b> <span className="opacity-70">→ Founded in Mumbai</span></div>
                  <div className="flex gap-2"><b>Research</b> <span className="opacity-70">→ Understanding India's wildlife</span></div>
                  <div className="flex gap-2"><b>Conservation</b> <span className="opacity-70">→ Protecting threatened species</span></div>
                  <div className="flex gap-2"><b>Education</b> <span className="opacity-70">→ Helping people understand nature</span></div>
                  <div className="flex gap-2"><b>Community</b> <span className="opacity-70">→ Bringing people into conservation</span></div>
                </div>
              </div>
            </div>
          </Page>,

          /* Page 4 - Left Illustration (Research) */
          !isMobile && <Page imagePage={true} imageSrc="/book/research.jpg" bookRef={bookRef} />,

          /* Page 5 - What Does BNHS Actually Do? */
          <Page number="2" bookRef={bookRef}>
            <div className="flex flex-col h-full">
              <h2 className="text-xl font-bold mb-4 text-[#F4C430]"><ShinyText text="From Research to Conservation" /></h2>
              <div className="space-y-3 overflow-y-auto no-scrollbar flex-1 pb-2 pr-1">
                <div className="flex gap-3">
                  <div className="bg-white/10 p-2 rounded-lg h-fit text-xl">🔬</div>
                  <div>
                    <h3 className="font-bold text-sm">Research</h3>
                    <p className="text-xs opacity-70 leading-relaxed">Scientists study species, ecosystems and environmental threats to understand what needs protection.</p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <div className="bg-white/10 p-2 rounded-lg h-fit text-xl">🦅</div>
                  <div>
                    <h3 className="font-bold text-sm">Species Conservation</h3>
                    <p className="text-xs opacity-70 leading-relaxed">BNHS works on threatened species and habitats across India, including birds, mammals, reptiles and marine ecosystems.</p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <div className="bg-white/10 p-2 rounded-lg h-fit text-xl">🌱</div>
                  <div>
                    <h3 className="font-bold text-sm">Habitat Conservation</h3>
                    <p className="text-xs opacity-70 leading-relaxed">Conservation begins with understanding the places wildlife depends on, from wetlands to grasslands.</p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <div className="bg-white/10 p-2 rounded-lg h-fit text-xl">📚</div>
                  <div>
                    <h3 className="font-bold text-sm">Education & Awareness</h3>
                    <p className="text-xs opacity-70 leading-relaxed">BNHS runs conservation education programmes, nature trails and courses.</p>
                  </div>
                </div>
              </div>
            </div>
          </Page>,

          /* Page 6 - Left Illustration (Volunteer) */
          !isMobile && <Page imagePage={true} imageSrc="/book/volunteer.jpg" bookRef={bookRef} />,

          /* Page 7 - Conservation Isn't Just About Scientists */
          <Page number="3" bookRef={bookRef}>
            <div className="flex flex-col h-full">
              <h2 className="text-2xl font-bold mb-4 text-[#F8F6E9] leading-tight">You Can Be Part of <br/><ShinyText text="Conservation" /></h2>
              <div className="overflow-y-auto no-scrollbar flex-1 flex flex-col">
                <p className="text-sm opacity-90 leading-relaxed mb-4">
                  You don't need to be a wildlife scientist to contribute.
                </p>
                <p className="text-sm opacity-90 leading-relaxed mb-6">
                  Conservation needs observers, volunteers, students, educators, photographers, communities and people who simply care about nature.
                </p>
                <div className="flex flex-col items-center justify-center gap-2 text-[#0B3D2E] font-medium text-sm bg-[#F4C430] p-4 rounded-xl border border-[#F4C430]/30 mt-auto shadow-inner text-center">
                  <div>Observe</div>
                  <div className="text-[#0B3D2E]/40">↓</div>
                  <div>Learn</div>
                  <div className="text-[#0B3D2E]/40">↓</div>
                  <div>Report</div>
                  <div className="text-[#0B3D2E]/40">↓</div>
                  <div>Participate</div>
                  <div className="text-[#0B3D2E]/40">↓</div>
                  <div className="font-bold">Protect</div>
                </div>
              </div>
            </div>
          </Page>,

          /* Page 8 - Left Illustration (Citizen Science) */
          !isMobile && <Page imagePage={true} imageSrc="/book/citizen.jpg" bookRef={bookRef} />,

          /* Page 9 - Find Your Way to Contribute */
          <Page number="4" bookRef={bookRef}>
            <div className="flex flex-col h-full">
              <h2 className="text-xl font-bold mb-4 text-[#F4C430]"><ShinyText text="How Can You Contribute?" /></h2>
              <div className="space-y-3 overflow-y-auto no-scrollbar flex-1 pb-2 pr-1">
                <div className="bg-white/10 p-3 rounded-xl border border-white/5">
                  <h3 className="font-bold text-sm flex items-center gap-2 mb-1">🐦 Citizen Science</h3>
                  <p className="text-xs opacity-70 leading-relaxed mb-2">Help collect observations and biodiversity data that can contribute to conservation research.</p>
                  <Link to="/explore-communities" className="text-xs font-semibold text-[#F4C430] hover:underline relative z-50 inline-block">Explore Citizen Science →</Link>
                </div>
                <div className="bg-white/10 p-3 rounded-xl border border-white/5">
                  <h3 className="font-bold text-sm flex items-center gap-2 mb-1">🌿 Volunteer</h3>
                  <p className="text-xs opacity-70 leading-relaxed mb-2">Give your time and skills to conservation programmes, education and outreach.</p>
                  <Link to="/explore-communities" className="text-xs font-semibold text-[#F4C430] hover:underline relative z-50 inline-block">Find Opportunities →</Link>
                </div>
                <div className="bg-white/10 p-3 rounded-xl border border-white/5">
                  <h3 className="font-bold text-sm flex items-center gap-2 mb-1">🎓 Learn</h3>
                  <p className="text-xs opacity-70 leading-relaxed mb-2">Join nature trails, workshops and courses to build your understanding of biodiversity.</p>
                  <Link to="/chatbot" className="text-xs font-semibold text-[#F4C430] hover:underline relative z-50 inline-block">Explore Learning →</Link>
                </div>
              </div>
            </div>
          </Page>,

          /* Page 10 - Left Illustration (Community) */
          !isMobile && <Page imagePage={true} imageSrc="/book/community.jpg" bookRef={bookRef} />,

          /* Page 11 - Meet the Community */
          <Page number="5" bookRef={bookRef}>
            <div className="flex flex-col h-full">
              <h2 className="text-2xl font-bold mb-4 text-[#F4C430] leading-tight"><ShinyText text="Conservation Works Better Together" /></h2>
              <div className="overflow-y-auto no-scrollbar flex-1 flex flex-col">
                <p className="text-sm opacity-90 leading-relaxed mb-4">
                  Wildlife doesn't exist in isolation and neither does conservation.
                </p>
                <p className="text-sm opacity-90 leading-relaxed mb-6">
                  Connect with people who share your interests, exchange knowledge, discover local initiatives and take action together.
                </p>
                <div className="flex flex-wrap gap-2 mb-6">
                  <span className="bg-white/10 px-3 py-1.5 rounded-full text-xs font-medium">🌳 Urban Biodiversity</span>
                  <span className="bg-white/10 px-3 py-1.5 rounded-full text-xs font-medium">🐦 Birdwatchers of India</span>
                  <span className="bg-white/10 px-3 py-1.5 rounded-full text-xs font-medium">🐘 Wildlife Conservation</span>
                  <span className="bg-white/10 px-3 py-1.5 rounded-full text-xs font-medium">🌊 Marine Conservation</span>
                </div>
                <Link to="/explore-communities" className="mt-auto flex justify-center items-center gap-2 w-full rounded-xl bg-[#F4C430] border border-[#F4C430]/20 py-3 text-[#0B3D2E] font-bold hover:bg-[#F4C430]/90 transition shadow-lg shrink-0">
                  Explore Communities <ArrowRight size={16} />
                </Link>
              </div>
            </div>
          </Page>,

          /* Page 12 - Left Illustration (Action) */
          <Page imagePage={true} imageSrc="/book/action.jpg" bookRef={bookRef} />

          /* Page 13 - From Interest to Action */
          <Page number="6" bookRef={bookRef}>
            <div className="flex flex-col h-full">
              <h2 className="text-2xl font-bold mb-4 text-[#F4C430]"><ShinyText text="See Something? Do Something." /></h2>
              <div className="overflow-y-auto no-scrollbar flex-1 flex flex-col">
                <div className="space-y-3 mb-6">
                  <div className="flex items-start gap-3">
                    <span className="text-lg">🐦</span>
                    <p className="text-sm opacity-90">You spot an injured bird.</p>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="text-lg">🌿</span>
                    <p className="text-sm opacity-90">You discover a local biodiversity hotspot.</p>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="text-lg">🦌</span>
                    <p className="text-sm opacity-90">You witness a wildlife concern.</p>
                  </div>
                </div>
                <p className="font-bold text-sm mb-4">What happens next?</p>
                <div className="text-[11px] font-bold opacity-70 tracking-wide uppercase mb-6 flex flex-wrap gap-2 text-center items-center justify-center">
                  Observe → Verify → Submit → Connect → Act
                </div>
                <div className="bg-white/10 p-4 rounded-xl border border-white/5 mt-auto relative z-50 shrink-0">
                  <h3 className="font-bold text-sm mb-1 text-[#F4C430]">My Submissions</h3>
                  <p className="text-xs opacity-80 leading-relaxed mb-3">Keep track of the observations, reports and contributions you've made through JeevSetu.</p>
                  <Link to="/my-submissions" className="text-xs font-bold hover:underline flex items-center text-[#F4C430] w-fit">View My Submissions <ArrowRight size={12} className="ml-1" /></Link>
                </div>
              </div>
            </div>
          </Page>,

          /* Page 14 - Left Illustration (Final) */
          <Page imagePage={true} imageSrc="/book/final.jpg" bookRef={bookRef} />

          /* Page 15 - Your JeevSetu */
          <Page number="7" bookRef={bookRef}>
            <div className="flex flex-col h-full py-2">
              <h2 className="text-2xl font-bold mb-6 text-[#F8F6E9] leading-tight">
                Your Connection to Wildlife <br/><ShinyText text="Starts Here." />
              </h2>
              
              <div className="overflow-y-auto no-scrollbar flex-1 flex flex-col">
                <div className="text-sm opacity-90 leading-relaxed mb-6 space-y-1 font-medium italic">
                  <p>Learn something.</p>
                  <p>Meet someone.</p>
                  <p>Notice something.</p>
                  <p>Contribute something.</p>
                </div>

                <p className="text-sm font-semibold text-[#F4C430] mb-8 leading-relaxed">
                  Every action can help build a stronger connection between people and the natural world.
                </p>

                <div className="flex flex-col gap-3 mb-6 relative z-50 shrink-0">
                  <Link to="/explore-communities" className="flex items-center gap-3 bg-white/10 p-3 rounded-xl border border-white/5 hover:bg-white/20 transition shadow-sm">
                    <div className="bg-[#F4C430] text-[#0B3D2E] p-2 rounded-lg"><Users size={18} /></div>
                    <span className="font-bold text-sm">Explore Communities</span>
                  </Link>
                  <Link to="/chatbot" className="flex items-center gap-3 bg-white/10 p-3 rounded-xl border border-white/5 hover:bg-white/20 transition shadow-sm">
                    <div className="bg-[#F4C430] text-[#0B3D2E] p-2 rounded-lg"><MessageCircle size={18} /></div>
                    <span className="font-bold text-sm">Ask JeevSetu</span>
                  </Link>
                </div>

                <p className="text-[10px] font-semibold opacity-50 text-center mt-auto tracking-widest uppercase shrink-0">
                  JeevSetu Bridging People & Wildlife
                </p>
              </div>
            </div>
          </Page>,
          
          /* Page 16 - Back Cover */
          <Page bookRef={bookRef}>
             <div className="flex flex-col items-center justify-center h-full">
               <img src="/jeevsetu-logo.png" alt="JeevSetu" className="w-40 h-auto brightness-0 invert mb-6 opacity-90 drop-shadow-md" />
               <p className="text-sm font-bold text-[#F4C430] tracking-widest uppercase mb-1">JeevSetu</p>
               <p className="text-[10px] font-medium opacity-70">© 2026 All Rights Reserved</p>
             </div>
          </Page>,
        
          ].filter(Boolean)}
        </HTMLFlipBook>
      </div>
      
      <p className="mt-8 text-[#0B3D2E]/40 text-sm font-medium animate-pulse tracking-wide z-10">
        Drag the corners or click left/right to flip pages
      </p>
    </div>
  );
}
