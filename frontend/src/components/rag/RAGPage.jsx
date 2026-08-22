import React, { useState } from "react";
import { searchBNHS, getNextSteps, getQuiz } from "./ragApi";

export default function RAGPage() {
  const [activeTab, setActiveTab] = useState("search");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState("");

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResults(null);
    try {
      if (activeTab === "search") {
        const data = await searchBNHS(query);
        setResults(data.results || []);
      } else if (activeTab === "next-steps") {
        const dummyResource = { title: query, content: "User requested action steps for this topic.", type: "General Topic" };
        const data = await getNextSteps(dummyResource);
        setResults(data.actions || []);
      } else if (activeTab === "quiz") {
        const data = await getQuiz(query);
        setResults(data.questions || []);
      }
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center py-10 font-sans">
      <div className="w-full max-w-4xl bg-white shadow-xl rounded-2xl overflow-hidden border border-gray-100">
        
        {/* Header */}
        <div className="bg-emerald-700 text-white p-8 text-center relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-full opacity-10 pointer-events-none">
             <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
                <defs>
                   <pattern id="leaf" width="40" height="40" patternUnits="userSpaceOnUse">
                      <path d="M20 0C20 11 11 20 0 20C11 20 20 29 20 40C20 29 29 20 40 20C29 20 20 11 20 0Z" fill="currentColor" />
                   </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#leaf)" />
             </svg>
          </div>
          <h1 className="text-4xl font-bold mb-2 relative z-10">BNHS Knowledge Hub</h1>
          <p className="text-emerald-100 text-lg relative z-10">Powered by Gemini AI & pgvector Search</p>
        </div>

        {/* Navigation Tabs */}
        <div className="flex border-b border-gray-200">
          <button 
            onClick={() => { setActiveTab("search"); setResults(null); }}
            className={`flex-1 py-4 text-center font-semibold transition-colors duration-200 ${activeTab === 'search' ? 'text-emerald-700 border-b-2 border-emerald-700 bg-emerald-50' : 'text-gray-500 hover:text-emerald-600 hover:bg-gray-50'}`}
          >
            🔍 Content Search
          </button>
          <button 
            onClick={() => { setActiveTab("next-steps"); setResults(null); }}
            className={`flex-1 py-4 text-center font-semibold transition-colors duration-200 ${activeTab === 'next-steps' ? 'text-emerald-700 border-b-2 border-emerald-700 bg-emerald-50' : 'text-gray-500 hover:text-emerald-600 hover:bg-gray-50'}`}
          >
            🚀 Next Steps
          </button>
          <button 
            onClick={() => { setActiveTab("quiz"); setResults(null); }}
            className={`flex-1 py-4 text-center font-semibold transition-colors duration-200 ${activeTab === 'quiz' ? 'text-emerald-700 border-b-2 border-emerald-700 bg-emerald-50' : 'text-gray-500 hover:text-emerald-600 hover:bg-gray-50'}`}
          >
            🧠 AI Quizzes
          </button>
        </div>

        {/* Main Content Area */}
        <div className="p-8">
          
          <form onSubmit={handleSearch} className="mb-8 relative">
            <input 
              type="text" 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={
                activeTab === "search" ? "Semantic Search: 'vulture conservation', 'birds in wetlands'..." :
                activeTab === "next-steps" ? "Enter a topic to generate LLM actionable steps..." :
                "Enter a topic to generate an LLM Quiz..."
              }
              className="w-full pl-6 pr-32 py-4 rounded-full bg-gray-100 border-transparent focus:bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 outline-none text-lg transition-all shadow-sm"
            />
            <button 
              type="submit" 
              disabled={loading || !query.trim()}
              className="absolute right-2 top-2 bottom-2 bg-emerald-600 hover:bg-emerald-700 text-white px-6 rounded-full font-medium transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center min-w-[120px]"
            >
              {loading ? (
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              ) : "Search"}
            </button>
          </form>

          {error && (
            <div className="bg-red-50 text-red-700 p-4 rounded-lg mb-6 border border-red-100">
              {error}
            </div>
          )}

          {/* Results Container */}
          <div className="space-y-6">
            
            {/* SEARCH RESULTS */}
            {activeTab === "search" && results && (
              results.length === 0 ? <p className="text-gray-500 text-center py-10">No results found.</p> :
              <div className="grid gap-6">
                <h3 className="text-xl font-bold text-gray-800 border-b pb-2">Vector Search Results</h3>
                {results.map((item, idx) => (
                  <a key={idx} href={item.bnhs_url || "#"} target="_blank" rel="noreferrer" className="group flex flex-col md:flex-row bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md hover:border-emerald-300 transition-all overflow-hidden relative">
                    {item.similarity_score !== undefined && item.similarity_score !== null && (
                      <div className="absolute top-2 right-2 bg-emerald-100 text-emerald-800 text-xs font-bold px-2 py-1 rounded-full z-10 shadow-sm border border-emerald-200">
                        {Math.round(item.similarity_score * 100)}% Match
                      </div>
                    )}
                    {item.image_url && (
                      <div className="md:w-48 h-48 md:h-auto bg-gray-100 shrink-0">
                        <img src={item.image_url} alt={item.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                      </div>
                    )}
                    <div className="p-6 flex-1 flex flex-col justify-center">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs font-bold uppercase tracking-wider text-emerald-600 bg-emerald-50 px-2 py-1 rounded-md">{item.content_type || 'Resource'}</span>
                        <span className="text-xs text-gray-400">{item.source || 'BNHS'}</span>
                      </div>
                      <h4 className="text-lg font-bold text-gray-900 mb-2 group-hover:text-emerald-700 transition-colors">{item.title}</h4>
                      <p className="text-gray-600 line-clamp-2">{item.summary}</p>
                    </div>
                  </a>
                ))}
              </div>
            )}

            {/* NEXT STEPS RESULTS */}
            {activeTab === "next-steps" && results && (
              results.length === 0 ? <p className="text-gray-500 text-center py-10">No recommended actions found for this topic.</p> :
              <div>
                <h3 className="text-xl font-bold text-gray-800 mb-6 border-b pb-2">AI Generated Actions</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {results.map((action, idx) => (
                    <a 
                      key={idx} 
                      href={action.direct_link || "#"} 
                      target="_blank" 
                      rel="noreferrer"
                      className="flex items-center p-5 rounded-xl border border-gray-200 hover:border-emerald-500 hover:shadow-md transition-all group bg-white"
                    >
                      <div className="w-12 h-12 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center text-xl font-bold mr-4 group-hover:bg-emerald-600 group-hover:text-white transition-colors">
                        {action.action_label === 'Learn' ? '📚' : action.action_label === 'Explore' ? '🌍' : action.action_label === 'Play' ? '🎮' : action.action_label === 'Take a quiz' ? '📝' : action.action_label === 'Advocate' ? '📢' : '🤝'}
                      </div>
                      <div>
                        <div className="text-sm font-bold text-emerald-600 uppercase tracking-wide">{action.action_label}</div>
                        <div className="text-gray-800 font-medium">{action.description}</div>
                      </div>
                    </a>
                  ))}
                </div>
              </div>
            )}

            {/* QUIZ RESULTS */}
            {activeTab === "quiz" && results && (
              results.length === 0 ? <p className="text-gray-500 text-center py-10">No quiz questions generated for this topic yet.</p> :
              <div className="space-y-8">
                <h3 className="text-xl font-bold text-gray-800 border-b pb-2">AI Generated Knowledge Test</h3>
                {results.map((q, qIdx) => (
                  <div key={qIdx} className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm relative group overflow-hidden">
                    <h4 className="text-lg font-bold text-gray-800 mb-4">{qIdx + 1}. {q.question}</h4>
                    <div className="space-y-3 relative z-10">
                      {q.options.map((opt, oIdx) => (
                        <div key={oIdx} className={`p-4 rounded-lg border transition-colors ${oIdx === q.correct_answer ? 'bg-emerald-50 border-emerald-200 opacity-0 group-hover:opacity-100' : 'bg-gray-50 border-gray-200'}`}>
                          <span className="font-bold text-gray-500 mr-3">{String.fromCharCode(65 + oIdx)}</span> {opt}
                          {oIdx === q.correct_answer && <span className="ml-2 text-emerald-600 font-bold opacity-0 group-hover:opacity-100 transition-opacity">✓ Correct</span>}
                        </div>
                      ))}
                    </div>
                    {/* Hover to reveal answer overlay */}
                    <div className="absolute inset-0 bg-white/60 backdrop-blur-sm z-20 flex items-center justify-center opacity-100 group-hover:opacity-0 transition-opacity duration-300 pointer-events-none">
                       <span className="bg-emerald-600 text-white px-6 py-3 rounded-full font-bold shadow-lg">Hover to reveal answer</span>
                    </div>
                    
                    <div className="mt-6 pt-4 border-t border-gray-100 opacity-0 group-hover:opacity-100 transition-opacity duration-300 relative z-10">
                      <p className="text-gray-600 text-sm"><strong className="text-gray-800">Explanation:</strong> {q.explanation}</p>
                      {q.source_reference && <p className="text-xs text-gray-400 mt-2">Source: {q.source_reference}</p>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}
