import { useState } from "react";

export default function SourceCard({
  source,
  index,
}) {
  const [expanded, setExpanded] =
    useState(false);

  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-start gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-emerald-50 text-sm font-bold text-emerald-700">
          {index + 1}
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <h4 className="font-semibold text-slate-900">
                {source.title}
              </h4>

              <p className="mt-1 text-xs text-slate-500">
                BNHS knowledge source
              </p>
            </div>

            <button
              type="button"
              onClick={() =>
                setExpanded(
                  (current) => !current,
                )
              }
              className="self-start rounded-lg px-2 py-1 text-xs font-semibold text-emerald-700 hover:bg-emerald-50"
            >
              {expanded
                ? "Hide excerpt"
                : "View excerpt"}
            </button>
          </div>

          {expanded && (
            <div className="mt-4 rounded-xl bg-slate-50 p-4">
              <p className="text-sm leading-7 text-slate-700">
                {source.excerpt ||
                  "No excerpt available."}
              </p>
            </div>
          )}
        </div>
      </div>
    </article>
  );
}