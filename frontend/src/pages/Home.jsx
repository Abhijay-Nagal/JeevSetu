import React, { useRef } from "react";
import HTMLFlipBook from "react-pageflip";
import { Link, Navigate } from "react-router-dom";
import { Leaf, Users, MessageCircle, FileText, Globe } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export const route = { path: "/" };

const Page = React.forwardRef((props, ref) => {
  return (
    <div 
      className="page bg-[#F8F6E9] shadow-[inset_0_0_20px_rgba(0,0,0,0.08)] border-r border-[#0B3D2E]/10 flex flex-col justify-center items-center text-center p-8 overflow-hidden relative" 
      ref={ref}
    >
      <div className="h-full w-full flex flex-col justify-center">
        {props.children}
      </div>
      {props.number && (
        <div className="absolute bottom-4 right-4 text-xs font-semibold opacity-40">
          {props.number}
        </div>
      )}
    </div>
  );
});

export default function Home() {
  const { user, loading } = useAuth();
  const bookRef = useRef(null);

  if (loading) return null;
  if (user) return <Navigate to="/home" replace />;

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-[#0B3D2E] py-12 text-[#0B3D2E] overflow-hidden">
      <div className="w-full max-w-5xl flex justify-between px-8 pb-8 text-[#F8F6E9] items-center absolute top-6">
         <img src="/jeevsetu-logo.png" className="h-8 brightness-0 invert" alt="JeevSetu" />
         <div className="flex gap-6">
           <Link to="/login" className="hover:underline font-medium text-sm">Log In</Link>
           <Link to="/signup" className="hover:underline font-medium text-sm">Sign Up</Link>
         </div>
      </div>
      
      <div className="mt-12 md:mt-16 z-10 perspective-1000">
        <HTMLFlipBook 
          width={400} 
          height={550} 
          size="stretch"
          minWidth={300}
          maxWidth={450}
          minHeight={450}
          maxHeight={650}
          showCover={true}
          className="mx-auto shadow-2xl drop-shadow-2xl book-container"
          ref={bookRef}
          useMouseEvents={true}
        >
          {/* Page 1 - Cover */}
          <Page>
            <div className="flex flex-col justify-between h-full py-4">
              <img src="/jeevsetu-logo.png" alt="JeevSetu" className="w-32 h-auto mx-auto mb-6" />
              <div>
                <h1 className="text-3xl font-bold mb-4 text-[#0B3D2E] px-4 leading-tight">Protect Wildlife. <br/>Empower Communities.</h1>
                <p className="text-sm opacity-80 mb-10 px-4 text-center">
                  A community-driven platform connecting people, conservation efforts, and wildlife to create a safer future for all.
                </p>
              </div>
              <div className="flex flex-col gap-3 px-8 mt-auto">
                <button 
                  onClick={(e) => { e.preventDefault(); bookRef.current?.pageFlip()?.flipNext(); }} 
                  className="rounded-full bg-[#0B3D2E] py-2.5 text-white font-medium hover:bg-[#0B3D2E]/90 transition"
                >
                  Explore Features
                </button>
              </div>
            </div>
          </Page>

          {/* Page 2 */}
          <Page>
            <Leaf className="mx-auto text-[#0B3D2E] mb-6" size={48} strokeWidth={1.5} />
            <h2 className="text-2xl font-bold mb-6 text-[#0B3D2E]">Welcome to JeevSetu</h2>
            <p className="text-sm opacity-80 leading-relaxed px-6 text-center">
              JeevSetu brings people together to understand, report, and take meaningful action for wildlife conservation. Whether you're sharing an observation, seeking guidance, or supporting a local initiative, every contribution helps.
            </p>
          </Page>

          {/* Page 3 */}
          <Page number="1">
            <Users className="mx-auto text-[#0B3D2E] mb-6" size={48} strokeWidth={1.5} />
            <h2 className="text-2xl font-bold mb-6 text-[#0B3D2E]">Explore Community</h2>
            <p className="text-sm opacity-80 leading-relaxed px-6 text-center mb-10">
              Connect, share, and discover wildlife conservation initiatives and stories from your community.
            </p>
            <button 
              onClick={(e) => { e.preventDefault(); bookRef.current?.pageFlip()?.flipNext(); }}
              className="inline-block rounded-full border-2 border-[#0B3D2E] px-8 py-2 text-sm text-[#0B3D2E] font-medium hover:bg-[#0B3D2E]/5 transition mx-auto"
            >
              Next
            </button>
          </Page>

          {/* Page 4 */}
          <Page number="2">
            <MessageCircle className="mx-auto text-[#0B3D2E] mb-6" size={48} strokeWidth={1.5} />
            <h2 className="text-2xl font-bold mb-6 text-[#0B3D2E]">JeevSetu Chatbot</h2>
            <p className="text-sm opacity-80 leading-relaxed px-6 text-center mb-10">
              Have a question about wildlife? Get quick guidance on wildlife, conservation, and responsible action.
            </p>
            <button 
              onClick={(e) => { e.preventDefault(); bookRef.current?.pageFlip()?.flipNext(); }}
              className="inline-block rounded-full border-2 border-[#0B3D2E] px-8 py-2 text-sm text-[#0B3D2E] font-medium hover:bg-[#0B3D2E]/5 transition mx-auto"
            >
              Next
            </button>
          </Page>

          {/* Page 5 */}
          <Page number="3">
            <FileText className="mx-auto text-[#0B3D2E] mb-6" size={48} strokeWidth={1.5} />
            <h2 className="text-2xl font-bold mb-6 text-[#0B3D2E]">My Submissions</h2>
            <p className="text-sm opacity-80 leading-relaxed px-6 text-center mb-10">
              Track the observations, reports, and contributions you've shared with the community.
            </p>
            <button 
              onClick={(e) => { e.preventDefault(); bookRef.current?.pageFlip()?.flipNext(); }}
              className="inline-block rounded-full border-2 border-[#0B3D2E] px-8 py-2 text-sm text-[#0B3D2E] font-medium hover:bg-[#0B3D2E]/5 transition mx-auto"
            >
              Next
            </button>
          </Page>

          {/* Page 6 */}
          <Page number="4">
            <Globe className="mx-auto text-[#0B3D2E] mb-8" size={48} strokeWidth={1.5} />
            <h2 className="text-2xl font-bold mb-10 text-[#0B3D2E]">Every Action Counts</h2>
            <div className="flex flex-col gap-6 text-center px-8 mx-auto w-full max-w-[240px]">
              <div>
                <div className="font-bold text-2xl text-[#0B3D2E] tracking-tight">1,240+</div>
                <div className="text-xs font-medium uppercase tracking-wider opacity-60 mt-1">Community Members</div>
              </div>
              <div>
                <div className="font-bold text-2xl text-[#0B3D2E] tracking-tight">386</div>
                <div className="text-xs font-medium uppercase tracking-wider opacity-60 mt-1">Wildlife Reports</div>
              </div>
              <div>
                <div className="font-bold text-2xl text-[#0B3D2E] tracking-tight">72</div>
                <div className="text-xs font-medium uppercase tracking-wider opacity-60 mt-1">Conservation Initiatives</div>
              </div>
            </div>
          </Page>

          {/* Page 7 */}
          <Page number="5">
            <div className="flex flex-col h-full justify-center pb-8 pt-6">
              <div>
                <h2 className="text-3xl font-bold mb-8 px-4 text-[#0B3D2E] leading-tight">Together, We Can Make a Difference</h2>
                <p className="text-sm opacity-80 leading-relaxed px-6 text-center mb-12">
                  Wildlife conservation begins when communities come together. Every observation, every report, and every action can help protect the wild.
                </p>
              </div>
              <div className="flex justify-center mt-auto">
                <Link to="/signup" className="rounded-full bg-[#F4C430] px-10 py-3 text-[#0B3D2E] font-bold hover:bg-[#F4C430]/90 transition shadow-lg text-lg">
                  Get Started
                </Link>
              </div>
            </div>
          </Page>
          
          {/* Page 8 - Back Cover */}
          <Page>
             <div className="flex flex-col items-center justify-center h-full opacity-30">
               <img src="/jeevsetu-logo.png" alt="JeevSetu" className="w-24 h-auto grayscale mb-4" />
               <p className="text-xs font-semibold">© 2026 JeevSetu</p>
             </div>
          </Page>
        </HTMLFlipBook>
      </div>
      
      <p className="mt-10 text-white/40 text-sm font-medium animate-pulse tracking-wide z-10">
        Drag the corners or click to flip pages
      </p>
    </div>
  );
}
