import { useEffect, useState } from "react"
import { Heart, MapPin, Loader2 } from "lucide-react"
import { api } from "../lib/api"

export const route = { path: "/submissions", layout: "app" }

const STATUS_STYLES = {
  submitted: { label: "Submitted", className: "bg-[#0B3D2E]/10 text-[#0B3D2E]" },
  under_review: { label: "Under review", className: "bg-[#F4C430]/20 text-[#8a6a0a]" },
  forwarded: { label: "Forwarded to researcher", className: "bg-[#81C784]/25 text-[#2E7D32]" },
  responded: { label: "Responded", className: "bg-[#0B3D2E] text-[#F8F6E9]" },
}

function StatusBadge({ status }) {
  const style = STATUS_STYLES[status] || STATUS_STYLES.submitted
  return (
    <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${style.className}`}>
      {style.label}
    </span>
  )
}

function MySubmissions() {
  const [submissions, setSubmissions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    api
      .myPosts()
      .then(setSubmissions)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="max-w-2xl">
      <h1 className="text-3xl font-semibold">My Submissions</h1>
      <p className="mt-2 opacity-70">Track the observations and reports you've shared.</p>

      {error && (
        <div className="mt-6 bg-red-50 text-red-700 p-4 rounded-xl border border-red-100">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-16 text-[#0B3D2E]/40">
          <Loader2 size={20} className="animate-spin" />
        </div>
      ) : submissions.length === 0 ? (
        <p className="text-[#0B3D2E]/50 py-10 text-center">
          You haven't posted anything yet -- share an observation from a community to see it here.
        </p>
      ) : (
        <div className="mt-6 space-y-3">
          {submissions.map((submission) => (
            <article
              key={submission.id}
              className="rounded-xl border border-[#0B3D2E]/10 bg-white p-4"
            >
              {submission.media_url && (
                <img
                  src={submission.media_url}
                  alt=""
                  className="mb-3 max-h-64 w-full rounded-lg object-cover"
                />
              )}

              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  {submission.species && (
                    <p className="font-semibold">{submission.species}</p>
                  )}
                  {submission.description && (
                    <p className="mt-1 text-sm text-[#0B3D2E]/80">{submission.description}</p>
                  )}
                </div>
                <StatusBadge status={submission.status} />
              </div>

              <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-[#0B3D2E]/50">
                {submission.location && (
                  <span className="flex items-center gap-1">
                    <MapPin size={12} />
                    {submission.location}
                  </span>
                )}
                <span className="flex items-center gap-1">
                  <Heart size={12} />
                  {submission.like_count}
                </span>
                <span>{new Date(submission.created_at).toLocaleDateString()}</span>
                {submission.assigned_researcher && (
                  <span>Assigned to {submission.assigned_researcher}</span>
                )}
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  )
}

export default MySubmissions
