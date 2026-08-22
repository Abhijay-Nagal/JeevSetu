import SourceCard from "./SourceCard";

function formatTime(date) {
  return new Intl.DateTimeFormat(
    "en-IN",
    {
      hour: "2-digit",
      minute: "2-digit",
    },
  ).format(date);
}

export default function ChatMessage({
  message,
}) {
  const isUser =
    message.role === "user";

  return (
    <div
      className={`flex w-full ${
        isUser
          ? "justify-end"
          : "justify-start"
      }`}
    >
      <div
        className={
          isUser
            ? "max-w-3xl rounded-3xl rounded-br-md bg-emerald-700 text-white shadow-sm"
            : "w-full max-w-4xl rounded-3xl rounded-bl-md border border-slate-200 bg-white text-slate-800 shadow-sm"
        }
      >
        <div className="px-5 py-4">
          <div className="mb-2 flex items-center justify-between gap-3">
            <span
              className={`text-xs font-bold uppercase tracking-wide ${
                isUser
                  ? "text-emerald-100"
                  : "text-emerald-700"
              }`}
            >
              {isUser
                ? "You"
                : "BNHS Guide"}
            </span>

            <span
              className={`text-[11px] ${
                isUser
                  ? "text-emerald-100"
                  : "text-slate-400"
              }`}
            >
              {formatTime(
                message.timestamp,
              )}
            </span>
          </div>

          <p className="whitespace-pre-wrap text-sm leading-7 md:text-base">
            {message.content}
          </p>
        </div>

        {!isUser &&
          message.sources &&
          message.sources.length > 0 && (
            <div className="border-t border-slate-100 px-5 py-5">
              <div className="mb-4 flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-blue-500" />

                <h3 className="text-sm font-bold text-slate-800">
                  Sources used
                </h3>

                <span className="rounded-full bg-blue-50 px-2 py-1 text-[11px] font-semibold text-blue-700">
                  {message.sources.length}
                </span>
              </div>

              <div className="space-y-3">
                {message.sources.map(
                  (source, index) => (
                    <SourceCard
                      key={`${source.title}-${index}`}
                      source={source}
                      index={index}
                    />
                  ),
                )}
              </div>
            </div>
          )}
      </div>
    </div>
  );
}