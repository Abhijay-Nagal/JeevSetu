const SUGGESTED_QUESTIONS = [
  "What does BNHS say about bird migration in India?",
  "What are the major conservation activities carried out by BNHS?",
  "What role does bird banding play in bird conservation?",
  "What does BNHS research say about wetlands and migratory birds?",
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