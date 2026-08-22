import {
  useState,
} from "react";

import ChatMessage from "./ChatMessage";
import SuggestedQuestions from "./SuggestedQuestions";
import { queryBNHS } from "./ragApi";

function createMessageId() {
  return `${Date.now()}-${Math.random()
    .toString(36)
    .slice(2)}`;
}

export default function RAGChat({
  accessToken = null,
}) {
  const [question, setQuestion] =
    useState("");

  const [messages, setMessages] =
    useState([]);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  async function submitQuestion(
    selectedQuestion,
  ) {
    const finalQuestion = (
      selectedQuestion ??
      question
    ).trim();

    if (
      !finalQuestion ||
      loading
    ) {
      return;
    }

    setQuestion("");
    setError("");

    const userMessage = {
      id: createMessageId(),
      role: "user",
      content: finalQuestion,
      timestamp: new Date(),
    };

    setMessages((previous) => [
      ...previous,
      userMessage,
    ]);

    setLoading(true);

    try {
      const response =
        await queryBNHS(
          finalQuestion,
          accessToken,
        );

      const assistantMessage = {
        id: createMessageId(),
        role: "assistant",
        content: response.answer,
        sources: response.sources,
        timestamp: new Date(),
      };

      setMessages((previous) => [
        ...previous,
        assistantMessage,
      ]);
    } catch (requestError) {
      const errorMessage =
        requestError instanceof Error
          ? requestError.message
          : "Something went wrong.";

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(event) {
    event.preventDefault();

    void submitQuestion();
  }

  function handleClearConversation() {
    setMessages([]);
    setQuestion("");
    setError("");
  }

  return (
    <div className="mx-auto w-full max-w-6xl">
      <section className="overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-xl shadow-slate-200/50">

        {/* Header */}
        <header className="border-b border-slate-100 bg-gradient-to-r from-emerald-50 via-white to-blue-50 px-6 py-7 md:px-8">
          <div className="flex flex-col gap-5 md:flex-row md:items-center md:justify-between">

            <div>
              <div className="mb-3 inline-flex items-center gap-2 rounded-full bg-emerald-100 px-3 py-1.5 text-xs font-bold text-emerald-800">
                <span className="h-2 w-2 rounded-full bg-emerald-600" />
                BNHS KNOWLEDGE ASSISTANT
              </div>

              <h1 className="text-3xl font-bold tracking-tight text-slate-900 md:text-4xl">
                Ask BNHS
              </h1>

              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600 md:text-base">
                Explore BNHS knowledge using
                answers grounded in retrieved
                sources from the configured
                knowledge base.
              </p>
            </div>

            {messages.length > 0 && (
              <button
                type="button"
                onClick={
                  handleClearConversation
                }
                className="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-600 transition hover:border-red-200 hover:bg-red-50 hover:text-red-700"
              >
                Clear conversation
              </button>
            )}

          </div>
        </header>

        {/* Conversation */}
        <div className="min-h-[520px] bg-slate-50/70 px-4 py-6 md:px-8">

          {messages.length === 0 ? (
            <div className="flex min-h-[430px] flex-col justify-center">
              <div className="mx-auto w-full max-w-3xl text-center">

                <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-100 text-3xl">
                  🐦
                </div>

                <h2 className="text-2xl font-bold text-slate-900">
                  What would you like to learn?
                </h2>

                <p className="mx-auto mt-3 max-w-xl text-sm leading-7 text-slate-600">
                  Ask a natural-language
                  question about biodiversity,
                  conservation, birds, research,
                  publications, or topics
                  available in the BNHS knowledge
                  base.
                </p>

                <SuggestedQuestions
                  disabled={loading}
                  onSelect={(selected) => {
                    void submitQuestion(
                      selected,
                    );
                  }}
                />

              </div>
            </div>
          ) : (
            <div className="space-y-5">

              {messages.map((message) => (
                <ChatMessage
                  key={message.id}
                  message={message}
                />
              ))}

              {loading && (
                <div className="flex justify-start">
                  <div className="rounded-3xl rounded-bl-md border border-slate-200 bg-white px-5 py-4 shadow-sm">

                    <div className="flex items-center gap-3">

                      <div className="flex gap-1">
                        <span className="h-2 w-2 animate-bounce rounded-full bg-emerald-500 [animation-delay:-0.3s]" />

                        <span className="h-2 w-2 animate-bounce rounded-full bg-emerald-500 [animation-delay:-0.15s]" />

                        <span className="h-2 w-2 animate-bounce rounded-full bg-emerald-500" />
                      </div>

                      <span className="text-sm text-slate-500">
                        Searching BNHS knowledge...
                      </span>

                    </div>

                  </div>
                </div>
              )}

            </div>
          )}

          {error && (
            <div className="mx-auto mt-5 max-w-4xl rounded-2xl border border-red-200 bg-red-50 p-4">
              <div className="flex items-start gap-3">

                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-red-100 font-bold text-red-700">
                  !
                </div>

                <div>
                  <p className="font-semibold text-red-900">
                    We couldn't complete that request.
                  </p>

                  <p className="mt-1 text-sm leading-6 text-red-700">
                    {error}
                  </p>
                </div>

              </div>
            </div>
          )}

        </div>

        {/* Input */}
        <footer className="border-t border-slate-200 bg-white p-4 md:p-6">

          <form
            onSubmit={handleSubmit}
            className="mx-auto max-w-4xl"
          >

            <div className="rounded-2xl border border-slate-300 bg-slate-50 p-2 shadow-inner transition focus-within:border-emerald-400 focus-within:ring-4 focus-within:ring-emerald-100">

              <div className="flex items-end gap-2">

                <textarea
                  value={question}
                  onChange={(event) =>
                    setQuestion(
                      event.target.value,
                    )
                  }
                  onKeyDown={(event) => {
                    if (
                      event.key ===
                        "Enter" &&
                      !event.shiftKey
                    ) {
                      event.preventDefault();

                      void submitQuestion();
                    }
                  }}
                  disabled={loading}
                  rows={2}
                  placeholder="Ask a question about BNHS..."
                  className="min-h-[74px] flex-1 resize-none bg-transparent px-3 py-2 text-sm leading-6 text-slate-900 outline-none placeholder:text-slate-400 disabled:cursor-not-allowed"
                />

                <button
                  type="submit"
                  disabled={
                    loading ||
                    question.trim()
                      .length === 0
                  }
                  className="rounded-xl bg-emerald-700 px-5 py-3 text-sm font-bold text-white transition hover:bg-emerald-800 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {loading
                    ? "Thinking..."
                    : "Ask BNHS"}
                </button>

              </div>

            </div>

            <p className="mt-2 text-center text-xs text-slate-400">
              Answers should be verified
              against the cited BNHS sources.
            </p>

          </form>

        </footer>

      </section>
    </div>
  );
}