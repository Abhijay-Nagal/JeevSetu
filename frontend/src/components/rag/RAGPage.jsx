import React, { useState } from "react";
import {
  Search,
  Compass,
  Brain,
  Loader2,
  BookOpen,
  Globe2,
  Gamepad2,
  PenSquare,
  Megaphone,
  Handshake,
  CheckCircle2,
  XCircle,
  ExternalLink,
  User,
  FileText,
} from "lucide-react";
import { api } from "../../lib/api";
import ShinyText from "../ui/ShinyText";
import SpotlightCard from "../ui/SpotlightCard";

const TABS = [
  { key: "search", label: "Content Search", icon: Search, placeholder: "Search: 'vulture conservation', 'birds in wetlands'..." },
  { key: "next-steps", label: "Explore", icon: Compass, placeholder: "Enter a topic to explore..." },
  { key: "quiz", label: "Quiz", icon: Brain, placeholder: "Enter a topic to generate a quiz..." },
];

const ACTION_ICONS = {
  Learn: BookOpen,
  Explore: Globe2,
  Play: Gamepad2,
  "Take a quiz": PenSquare,
  Advocate: Megaphone,
};

export default function RAGPage() {
  const [activeTab, setActiveTab] = useState("search");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState("");
  const [quizAnswers, setQuizAnswers] = useState({});

  const currentTab = TABS.find((tab) => tab.key === activeTab);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResults(null);
    setQuizAnswers({});
    try {
      if (activeTab === "search") {
        const data = await api.searchKnowledgeHub(query);
        setResults(data.results || []);
      } else if (activeTab === "next-steps") {
        const dummyResource = { title: query, content: "User requested action steps for this topic.", type: "General Topic" };
        const data = await api.getNextSteps(dummyResource);
        setResults(data.actions || []);
      } else if (activeTab === "quiz") {
        const data = await api.getQuiz(query);
        setResults(data.questions || []);
      }
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  return (
    <div className="w-full max-w-4xl mx-auto bg-white/80 backdrop-blur-sm rounded-2xl overflow-hidden border border-[#0B3D2E]/10 shadow-sm relative z-0">
      <div className="absolute top-0 right-0 w-64 h-64 bg-[#F4C430]/10 rounded-full blur-3xl -z-10 animate-pulse"></div>
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-[#0B3D2E]/5 rounded-full blur-3xl -z-10"></div>

      {/* Header */}
      <div className="px-6 py-5 sm:px-8 sm:py-7 border-b border-[#0B3D2E]/5">
        <h1 className="text-3xl sm:text-4xl font-bold tracking-tight">
          <ShinyText text="BNHS Knowledge Hub" variant="green" />
        </h1>
        <p className="text-[#0B3D2E]/70 mt-2 text-base sm:text-lg">Search, learn, and test your knowledge of Indian wildlife</p>
      </div>

      {/* Navigation Tabs */}
      <div className="flex flex-col sm:flex-row gap-2 bg-[#0B3D2E]/5 p-2 overflow-x-auto hide-scrollbar">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.key;
          return (
            <button
              key={tab.key}
              onClick={() => { setActiveTab(tab.key); setResults(null); setError(""); setQuizAnswers({}); }}
              className={`flex-1 min-w-[140px] flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-medium transition ${
                isActive
                  ? "bg-[#F4C430] text-[#0B3D2E]"
                  : "text-[#0B3D2E]/60 hover:bg-[#0B3D2E]/10 hover:text-[#0B3D2E]"
              }`}
            >
              <Icon size={17} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Main Content Area */}
      <div className="p-4 sm:p-8">

          <form onSubmit={handleSearch} className="mb-6 flex flex-col sm:flex-row gap-3">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={currentTab.placeholder}
              className="flex-1 px-5 py-3 rounded-xl bg-[#F8F6E9] border border-[#0B3D2E]/15 focus:bg-white focus:border-[#F4C430] focus:ring-2 focus:ring-[#F4C430]/30 outline-none text-base transition-all"
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="bg-[#F4C430] hover:bg-[#e0b422] text-[#0B3D2E] px-6 py-3 rounded-xl font-semibold transition-colors disabled:bg-[#0B3D2E]/10 disabled:text-[#0B3D2E]/40 disabled:cursor-not-allowed flex items-center justify-center min-w-[110px]"
            >
              {loading ? <Loader2 size={18} className="animate-spin" /> : "Search"}
            </button>
          </form>

          {error && (
            <div className="bg-red-50 text-red-700 p-4 rounded-xl mb-6 border border-red-100">
              {error}
            </div>
          )}

          {/* Results Container */}
          <div className="space-y-6">

            {/* SEARCH RESULTS */}
            {activeTab === "search" && results && (
              results.length === 0 ? <p className="text-[#0B3D2E]/50 text-center py-10">No results found.</p> :
              <div className="grid gap-4">
                <h3 className="text-lg font-bold border-b border-[#0B3D2E]/10 pb-2">Search results</h3>
                {results.map((item, idx) => (
                  <SpotlightCard key={idx} className="p-0 border-none bg-transparent hover:translate-y-0 shadow-none hover:shadow-none mb-2 group">
                    <a
                      href={item.bnhs_url || "#"}
                      target="_blank"
                      rel="noreferrer"
                      className="flex flex-col md:flex-row bg-white rounded-xl border border-[#0B3D2E]/10 group-hover:border-[#0B3D2E]/20 transition-colors overflow-hidden relative"
                    >
                    {item.similarity_score !== undefined && item.similarity_score !== null && (
                      <div className="absolute top-3 right-3 bg-[#81C784]/20 text-[#0B3D2E] text-xs font-bold px-2 py-1 rounded-full z-10">
                        {Math.round(item.similarity_score * 100)}% match
                      </div>
                    )}
                    {item.image_url && (
                      <div className="md:w-48 h-48 md:h-auto bg-[#F8F6E9] shrink-0">
                        <img src={item.image_url} alt={item.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                      </div>
                    )}
                    <div className="p-6 flex-1 flex flex-col justify-center">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs font-bold uppercase tracking-wider text-[#2E7D32] bg-[#81C784]/15 px-2 py-1 rounded-md">{item.content_type || "Resource"}</span>
                        <span className="text-xs text-[#0B3D2E]/40">{item.source || "BNHS"}</span>
                      </div>
                      <h4 className="text-lg font-bold mb-2 group-hover:text-[#2E7D32] transition-colors flex items-center gap-2">
                        {item.title}
                        <ExternalLink size={14} className="opacity-0 group-hover:opacity-60 transition-opacity" />
                      </h4>
                      <p className="text-[#0B3D2E]/60 line-clamp-2">{item.summary}</p>
                      {(item.author || item.file_name) && (
                        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-3 pt-3 border-t border-[#0B3D2E]/10 text-xs text-[#0B3D2E]/50">
                          {item.author && (
                            <span className="flex items-center gap-1">
                              <User size={12} />
                              {item.author}
                            </span>
                          )}
                          {item.file_name && (
                            <span className="flex items-center gap-1">
                              <FileText size={12} />
                              {item.file_name}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                    </a>
                  </SpotlightCard>
                ))}
              </div>
            )}

            {/* NEXT STEPS RESULTS */}
            {activeTab === "next-steps" && results && (
              results.length === 0 ? <p className="text-[#0B3D2E]/50 text-center py-10">No recommended actions found for this topic.</p> :
              <div>
                <h3 className="text-lg font-bold mb-4 border-b border-[#0B3D2E]/10 pb-2">Recommended actions</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {results.map((action, idx) => {
                    const Icon = ACTION_ICONS[action.action_label] || Handshake;
                    return (
                      <SpotlightCard key={idx} className="p-0 border-none bg-transparent hover:translate-y-0 shadow-none hover:shadow-none group h-full">
                        <a
                          href={action.direct_link || "#"}
                          target="_blank"
                          rel="noreferrer"
                          className="flex items-center p-5 rounded-xl border border-[#0B3D2E]/10 group-hover:border-[#0B3D2E]/20 transition-colors bg-white h-full"
                        >
                        <div className="w-11 h-11 shrink-0 rounded-full bg-[#81C784]/20 text-[#2E7D32] flex items-center justify-center mr-4 group-hover:bg-[#F4C430] group-hover:text-[#0B3D2E] transition-colors">
                          <Icon size={20} />
                        </div>
                        <div>
                          <div className="text-xs font-bold text-[#2E7D32] uppercase tracking-wide">{action.action_label}</div>
                          <div className="text-[#0B3D2E] font-medium">{action.description}</div>
                        </div>
                        </a>
                      </SpotlightCard>
                    );
                  })}
                </div>
              </div>
            )}

            {/* QUIZ RESULTS */}
            {activeTab === "quiz" && results && (
              results.length === 0 ? <p className="text-[#0B3D2E]/50 text-center py-10">No quiz questions generated for this topic yet.</p> :
              <div className="space-y-6">
                <h3 className="text-lg font-bold border-b border-[#0B3D2E]/10 pb-2">Knowledge check</h3>
                {results.map((q, qIdx) => {
                  const selected = quizAnswers[qIdx];
                  const attempted = selected !== undefined;
                  return (
                    <SpotlightCard key={qIdx} className="p-0 border-none bg-transparent hover:translate-y-0 shadow-none hover:shadow-none mb-2">
                      <div className="bg-white rounded-xl border border-[#0B3D2E]/10 p-6 transition-colors hover:border-[#0B3D2E]/20">
                        <h4 className="text-base font-bold mb-4">{qIdx + 1}. {q.question}</h4>
                      <div className="space-y-2.5">
                        {q.options.map((opt, oIdx) => {
                          const isCorrect = oIdx === q.correct_answer;
                          const isSelected = oIdx === selected;
                          let stateClasses = "bg-[#F8F6E9] border-[#0B3D2E]/10 hover:border-[#F4C430] cursor-pointer";
                          if (attempted) {
                            if (isCorrect) stateClasses = "bg-[#81C784]/15 border-[#81C784]/40";
                            else if (isSelected) stateClasses = "bg-red-50 border-red-200";
                            else stateClasses = "bg-[#F8F6E9] border-[#0B3D2E]/10 opacity-60";
                          }
                          return (
                            <button
                              key={oIdx}
                              type="button"
                              disabled={attempted}
                              onClick={() => setQuizAnswers((prev) => ({ ...prev, [qIdx]: oIdx }))}
                              className={`w-full flex items-center gap-3 p-3.5 rounded-lg border text-sm text-left transition-colors ${stateClasses}`}
                            >
                              <span className="font-bold text-[#0B3D2E]/40">{String.fromCharCode(65 + oIdx)}</span>
                              <span className="flex-1">{opt}</span>
                              {attempted && isCorrect && <CheckCircle2 size={16} className="text-[#2E7D32] shrink-0" />}
                              {attempted && isSelected && !isCorrect && <XCircle size={16} className="text-red-500 shrink-0" />}
                            </button>
                          );
                        })}
                      </div>

                      {attempted && (
                        <div className="mt-5 pt-4 border-t border-[#0B3D2E]/10">
                          <p className="text-sm text-[#0B3D2E]/70"><strong className="text-[#0B3D2E]">Explanation:</strong> {q.explanation}</p>
                          {q.source_reference && <p className="text-xs text-[#0B3D2E]/40 mt-2">Source: {q.source_reference}</p>}
                        </div>
                      )}
                      </div>
                    </SpotlightCard>
                  );
                })}
              </div>
            )}
          </div>

      </div>
    </div>
  );
}
