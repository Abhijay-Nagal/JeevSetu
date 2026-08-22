import { useEffect, useState } from "react"
import { Coins, ArrowUpRight } from "lucide-react"
import { api } from "../lib/api"

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

function Rewards() {
  const [wallet, setWallet] = useState(null)
  const [error, setError] = useState("")

  useEffect(() => {
    api
      .getWallet()
      .then(setWallet)
      .catch((err) => setError(err.message))
  }, [])

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
