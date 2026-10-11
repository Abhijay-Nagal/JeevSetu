const SUGGESTED_QUESTIONS = [
  "Why are India's vultures endangered, and what is BNHS doing about it?",
  "Tell me about the Great Indian Bustard",
  "Who was Dr. Salim Ali?",
  "How can I become a BNHS member?",
];

export default function SuggestedQuestions({
  onSelect,
  disabled = false,
}) {
  return (
    <div className="mt-8 w-full">
      <div className="mb-4 flex items-center gap-2">
        <span className="h-2 w-2 rounded-full bg-emerald-600" />

        <p className="text-sm font-semibold text-slate-700">
          Try asking BNHS
        </p>
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        {SUGGESTED_QUESTIONS.map(
          (question) => (
            <button
              key={question}
              type="button"
              disabled={disabled}
              onClick={() =>
                onSelect(question)
              }
              className="group rounded-2xl border border-slate-200 bg-white p-4 text-left shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-emerald-300 hover:shadow-md disabled:cursor-not-allowed disabled:opacity-50"
            >
              <div className="flex items-start gap-3">
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-emerald-50 font-bold text-emerald-700">
                  ?
                </span>

                <span className="text-sm leading-6 text-slate-700">
                  {question}
                </span>
              </div>
            </button>
          ),
        )}
      </div>
    </div>
  );
}