import { useEffect, useState } from "react"
import { Heart, MapPin, Loader2 } from "lucide-react"
import { api } from "../lib/api"
import ShinyText from "../components/ui/ShinyText"

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
    <div className="max-w-3xl relative p-8 rounded-3xl bg-gradient-to-br from-[#0B3D2E]/5 to-transparent overflow-hidden border border-[#0B3D2E]/5 shadow-sm">
      <div className="absolute -top-24 -right-24 w-96 h-96 bg-[#F4C430]/15 rounded-full blur-[80px] -z-10 animate-pulse"></div>
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-[#0B3D2E]/10 rounded-full blur-[80px] -z-10"></div>

      <div className="mb-8">
        <h1 className="text-4xl font-bold tracking-tight"><ShinyText text="My Submissions" variant="green" /></h1>
        <p className="mt-3 text-lg opacity-80 text-[#0B3D2E]">Track the observations and reports you've shared.</p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 text-red-700 p-4 rounded-xl border border-red-100 font-medium relative z-10">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-16 text-[#0B3D2E]/40 relative z-10">
          <Loader2 size={32} className="animate-spin" />
        </div>
      ) : submissions.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-[#0B3D2E]/20 bg-white/50 p-10 text-center relative z-10">
          <p className="text-[#0B3D2E]/60 text-lg">
            You haven't posted anything yet — share an observation from a community to see it here.
          </p>
        </div>
      ) : (
        <div className="space-y-5 relative z-10">
          {submissions.map((submission) => (
            <article
              key={submission.id}
              className="rounded-2xl border border-[#0B3D2E]/10 bg-white p-5 hover:border-[#0B3D2E]/30 transition-all shadow-sm hover:shadow-md overflow-hidden"
            >
              <div className="flex flex-col sm:flex-row gap-5">
                {submission.media_url && (
                  <div className="sm:w-48 shrink-0">
                    <img
                      src={submission.media_url}
                      alt=""
                      className="h-48 sm:h-full w-full rounded-xl object-cover"
                    />
                  </div>
                )}

                <div className="flex flex-1 flex-col justify-between py-1">
                  <div>
                    <div className="flex items-start justify-between gap-3 mb-2">
                      <div className="min-w-0">
                        {submission.species && (
                          <p className="font-bold text-lg text-[#0B3D2E]">{submission.species}</p>
                        )}
                        {!submission.species && submission.description && (
                          <p className="font-bold text-lg text-[#0B3D2E] truncate">Observation</p>
                        )}
                      </div>
                      <StatusBadge status={submission.status} />
                    </div>
                    {submission.description && (
                      <p className="text-sm text-[#0B3D2E]/80 line-clamp-3 leading-relaxed mb-4">{submission.description}</p>
                    )}
                  </div>

                  <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-xs font-semibold text-[#0B3D2E]/60 bg-[#0B3D2E]/5 rounded-lg p-2.5">
                    {submission.location && (
                      <span className="flex items-center gap-1.5 text-[#0B3D2E]">
                        <MapPin size={14} className="text-[#2E7D32]" />
                        {submission.location}
                      </span>
                    )}
                    <span className="flex items-center gap-1.5 text-[#0B3D2E]">
                      <Heart size={14} className="text-red-500" />
                      {submission.like_count}
                    </span>
                    <span>{new Date(submission.created_at).toLocaleDateString()}</span>
                    {submission.assigned_researcher && (
                      <span className="text-[#2E7D32]">Assigned to {submission.assigned_researcher}</span>
                    )}
                  </div>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  )
}

export default MySubmissions
