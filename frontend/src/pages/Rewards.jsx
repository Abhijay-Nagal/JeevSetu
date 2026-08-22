import { useEffect, useState } from "react"
import { Coins, ArrowUpRight, Flame, Snowflake, CheckCircle2, XCircle, Loader2 } from "lucide-react"
import { api } from "../lib/api"
import { useWallet } from "../context/WalletContext"

export const route = { path: "/rewards", layout: "app" }

const REASON_LABELS = {
  daily_question_correct: "Daily question — correct answer",
  streak_milestone: "Streak milestone bonus",
  community_quiz_score: "Community quiz — correct answers",
  community_quiz_placement: "Community quiz — leaderboard placement",
  post_created: "Post created",
  post_liked: "Your post was liked",
  community_joined: "Joined a community",
  community_created: "Created a community",
}

function StreakBadges({ streak }) {
  if (!streak) return null
  return (
    <div className="flex items-center gap-4 text-sm">
      <span className="flex items-center gap-1.5 font-semibold">
        <Flame size={16} className="text-[#F4C430]" />
        {streak.current_streak}-day streak
      </span>
      {streak.freezes_available > 0 && (
        <span className="flex items-center gap-1.5 text-[#0B3D2E]/60">
          <Snowflake size={14} />
          {streak.freezes_available} freeze{streak.freezes_available === 1 ? "" : "s"} banked
        </span>
      )}
    </div>
  )
}

function DailyQuestionCard({ onAnswered }) {
  const [question, setQuestion] = useState(null)
  const [selected, setSelected] = useState(undefined)
  const [result, setResult] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    api
      .getDailyQuestion()
      .then(setQuestion)
      .catch((err) => setError(err.message))
  }, [])

  const handleSelect = async (index) => {
    if (submitting || result) return
    setSelected(index)
    setSubmitting(true)
    setError("")
    try {
      const data = await api.answerDailyQuestion(index)
      setResult(data)
      onAnswered?.()
    } catch (err) {
      setError(err.message)
      setSelected(undefined)
    }
    setSubmitting(false)
  }

  if (error) {
    return <div className="bg-red-50 text-red-700 p-4 rounded-xl border border-red-100">{error}</div>
  }

  if (!question) {
    return (
      <div className="flex items-center justify-center py-10 text-[#0B3D2E]/40">
        <Loader2 size={20} className="animate-spin" />
      </div>
    )
  }

  const alreadyAnswered = question.already_answered && !result

  return (
    <div className="rounded-2xl border border-[#0B3D2E]/10 bg-white p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold">Today's question</h3>
        <StreakBadges streak={result?.streak || question.streak} />
      </div>

      {alreadyAnswered ? (
        <p className="text-[#0B3D2E]/60 py-4">
          You've already answered today's question — come back tomorrow to keep your streak alive.
        </p>
      ) : (
        <>
          <p className="font-medium mb-4">{question.question}</p>
          <div className="space-y-2.5">
            {question.options.map((opt, idx) => {
              const attempted = Boolean(result)
              const isCorrect = attempted && idx === result.correct_answer
              const isWrongSelection = attempted && idx === selected && !isCorrect
              let stateClasses = "bg-[#F8F6E9] border-[#0B3D2E]/10 hover:border-[#F4C430] cursor-pointer"
              if (attempted) {
                if (isCorrect) stateClasses = "bg-[#81C784]/15 border-[#81C784]/40"
                else if (isWrongSelection) stateClasses = "bg-red-50 border-red-200"
                else stateClasses = "bg-[#F8F6E9] border-[#0B3D2E]/10 opacity-60"
              }
              return (
                <button
                  key={idx}
                  type="button"
                  disabled={attempted || submitting}
                  onClick={() => handleSelect(idx)}
                  className={`w-full flex items-center gap-3 p-3.5 rounded-lg border text-sm text-left transition-colors ${stateClasses}`}
                >
                  <span className="font-bold text-[#0B3D2E]/40">{String.fromCharCode(65 + idx)}</span>
                  <span className="flex-1">{opt}</span>
                  {isCorrect && <CheckCircle2 size={16} className="text-[#2E7D32] shrink-0" />}
                  {isWrongSelection && <XCircle size={16} className="text-red-500 shrink-0" />}
                </button>
              )
            })}
          </div>

          {result && (
            <div className="mt-5 pt-4 border-t border-[#0B3D2E]/10">
              <p className="text-sm font-semibold text-[#2E7D32]">
                {result.is_correct ? `Correct! +${result.coins_awarded} coins` : "Not quite — no coins this time."}
              </p>
              {result.explanation && (
                <p className="text-sm text-[#0B3D2E]/70 mt-1">{result.explanation}</p>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}

function Rewards() {
  const { wallet, refreshWallet } = useWallet()
  const [error, setError] = useState("")

  return (
    <div className="max-w-2xl">
      <h1 className="text-3xl font-semibold">Rewards</h1>
      <p className="mt-2 opacity-70">
        Earn coins by answering the daily question, keeping your streak alive, and joining in
        with communities.
      </p>

      {error && (
        <div className="mt-6 bg-red-50 text-red-700 p-4 rounded-xl border border-red-100">
          {error}
        </div>
      )}

      <div className="mt-8 flex items-center gap-4 rounded-2xl bg-[#0B3D2E] text-[#F8F6E9] px-8 py-6">
        <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-[#F4C430] text-[#0B3D2E]">
          <Coins size={26} />
        </div>
        <div>
          <p className="text-sm text-[#F8F6E9]/70">Your balance</p>
          <p className="text-3xl font-bold">
            {wallet ? wallet.coin_balance.toLocaleString() : "..."} coins
          </p>
        </div>
      </div>

      <div className="mt-6">
        <DailyQuestionCard onAnswered={refreshWallet} />
      </div>

      <h2 className="mt-8 mb-3 text-lg font-bold">Recent activity</h2>
      {wallet && wallet.recent_transactions.length === 0 && (
        <p className="text-[#0B3D2E]/50 py-6 text-center">
          No activity yet — answer today's question to start earning coins.
        </p>
      )}
      <div className="space-y-2">
        {wallet?.recent_transactions.map((tx) => (
          <div
            key={tx.id}
            className="flex items-center justify-between rounded-xl border border-[#0B3D2E]/10 bg-white px-5 py-3.5"
          >
            <div className="flex items-center gap-3">
              <ArrowUpRight size={16} className="text-[#2E7D32]" />
              <span className="text-sm font-medium">{REASON_LABELS[tx.reason] || tx.reason}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm font-bold text-[#2E7D32]">+{tx.amount}</span>
              <span className="text-xs text-[#0B3D2E]/40">
                {new Date(tx.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Rewards
