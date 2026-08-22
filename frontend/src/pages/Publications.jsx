import { useEffect, useState } from "react"
import { FlaskConical, Search, Loader2, ExternalLink } from "lucide-react"
import { api } from "../lib/api"
import { uploadObservationImage } from "../lib/storage"
import ShinyText from "../components/ui/ShinyText"

export const route = { path: "/publications", layout: "app" }

function Publications() {
  const [title, setTitle] = useState("")
  const [abstract, setAbstract] = useState("")
  const [description, setDescription] = useState("")
  const [species, setSpecies] = useState("")
  const [location, setLocation] = useState("")
  const [file, setFile] = useState(null)

  const [relatedResults, setRelatedResults] = useState(null)

  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState(false)

  const [submissions, setSubmissions] = useState([])
  const [loadingSubmissions, setLoadingSubmissions] = useState(true)

  useEffect(() => {
    api
      .myResearchSubmissions()
      .then(setSubmissions)
      .finally(() => setLoadingSubmissions(false))
  }, [])

  async function handleSubmit(event) {
    event.preventDefault()
    setSubmitting(true)
    setError("")
    setSuccess(false)
    setRelatedResults(null)
    try {
      // Hit the RAG pipeline first -- check what BNHS already has on this
      // topic -- then do the actual submission. Informational only, doesn't
      // block or gate saving the submission.
      const related = await api.checkRelatedRecords(abstract.trim())

      let mediaUrl = null
      if (file) {
        mediaUrl = await uploadObservationImage(file)
      }

      const submission = await api.submitResearch({
        title: title.trim(),
        abstract: abstract.trim(),
        description: description.trim() || null,
        species: species.trim() || null,
        location: location.trim() || null,
        media_url: mediaUrl,
      })

      setSubmissions((prev) => [submission, ...prev])
      setRelatedResults(related.results || [])
      setTitle("")
      setAbstract("")
      setDescription("")
      setSpecies("")
      setLocation("")
      setFile(null)
      setSuccess(true)
    } catch (err) {
      setError(err.message)
    }
    setSubmitting(false)
  }

  return (
    <div className="max-w-3xl relative p-8 rounded-3xl bg-gradient-to-br from-[#0B3D2E]/5 to-transparent overflow-hidden border border-[#0B3D2E]/5 shadow-sm">
      <div className="absolute -top-24 -right-24 w-96 h-96 bg-[#F4C430]/15 rounded-full blur-[80px] -z-10 animate-pulse"></div>
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-[#0B3D2E]/10 rounded-full blur-[80px] -z-10"></div>

      <div className="mb-8">
        <h1 className="text-4xl font-bold tracking-tight flex items-center gap-3">
          <div className="p-3 bg-[#0B3D2E]/10 rounded-2xl text-[#2E7D32]">
            <FlaskConical size={28} />
          </div>
          <ShinyText text="Publications" variant="green" />
        </h1>
        <p className="mt-3 text-lg opacity-80 text-[#0B3D2E]">
          Found something new? Submit your research to BNHS — we'll check what's already known
          about it before you send it in.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="relative z-10 space-y-5 rounded-2xl border border-[#0B3D2E]/10 bg-white/70 backdrop-blur-md p-6 sm:p-8 shadow-sm">
        <div>
          <label className="block text-sm font-semibold mb-1.5 text-[#0B3D2E]">Title</label>
          <input
            type="text"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full rounded-xl border border-[#0B3D2E]/20 bg-white px-4 py-3 text-sm outline-none transition focus:border-[#F4C430] focus:ring-2 focus:ring-[#F4C430]/30"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold mb-1.5 text-[#0B3D2E]">Abstract</label>
          <textarea
            required
            rows={4}
            value={abstract}
            onChange={(e) => setAbstract(e.target.value)}
            placeholder="Summarize your finding — checked against BNHS's existing records when you submit."
            className="w-full resize-none rounded-xl border border-[#0B3D2E]/20 bg-white px-4 py-3 text-sm outline-none transition focus:border-[#F4C430] focus:ring-2 focus:ring-[#F4C430]/30"
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-semibold mb-1.5 text-[#0B3D2E]">Species (optional)</label>
            <input
              type="text"
              value={species}
              onChange={(e) => setSpecies(e.target.value)}
              className="w-full rounded-xl border border-[#0B3D2E]/20 bg-white px-4 py-3 text-sm outline-none transition focus:border-[#F4C430] focus:ring-2 focus:ring-[#F4C430]/30"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold mb-1.5 text-[#0B3D2E]">Location (optional)</label>
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-full rounded-xl border border-[#0B3D2E]/20 bg-white px-4 py-3 text-sm outline-none transition focus:border-[#F4C430] focus:ring-2 focus:ring-[#F4C430]/30"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-semibold mb-1.5 text-[#0B3D2E]">Full write-up (optional)</label>
          <textarea
            rows={4}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full resize-none rounded-xl border border-[#0B3D2E]/20 bg-white px-4 py-3 text-sm outline-none transition focus:border-[#F4C430] focus:ring-2 focus:ring-[#F4C430]/30"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold mb-1.5 text-[#0B3D2E]">Supporting document or image (optional)</label>
          <div className="relative">
            <input
              type="file"
              accept="application/pdf,image/*"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              className="block w-full text-sm text-[#0B3D2E]/70 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-[#0B3D2E]/10 file:text-[#0B3D2E] hover:file:bg-[#0B3D2E]/20 transition-colors"
            />
          </div>
        </div>

        {error && <p className="text-sm font-medium text-red-600 bg-red-50 p-3 rounded-lg border border-red-100">{error}</p>}
        {success && <p className="text-sm font-medium text-[#2E7D32] bg-[#81C784]/20 p-3 rounded-lg border border-[#81C784]/40">Submitted successfully! BNHS will follow up on this.</p>}

        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-xl bg-[#0B3D2E] px-4 py-3.5 text-sm font-bold tracking-wide text-white transition hover:bg-[#0B3D2E]/90 disabled:opacity-70 disabled:cursor-not-allowed shadow-md hover:shadow-lg mt-2"
        >
          {submitting ? (
            <span className="flex items-center justify-center gap-2">
              <Loader2 size={18} className="animate-spin" />
              Checking BNHS records & submitting...
            </span>
          ) : (
            "Submit to BNHS"
          )}
        </button>
      </form>

      {relatedResults && (
        <div className="mt-6 relative z-10 rounded-2xl border border-[#0B3D2E]/15 bg-[#F8F6E9] p-6 shadow-sm">
          <p className="text-base font-bold flex items-center gap-2 mb-4 text-[#0B3D2E]">
            <Search size={18} className="text-[#2E7D32]" />
            {relatedResults.length === 0 ? "No closely related BNHS records found" : "BNHS already has related records"}
          </p>
          <div className="space-y-3">
            {relatedResults.map((item, idx) => (
              <a
                key={idx}
                href={item.bnhs_url || "#"}
                target="_blank"
                rel="noreferrer"
                className="group block rounded-xl bg-white px-5 py-4 border border-[#0B3D2E]/10 hover:border-[#F4C430] hover:shadow-md transition-all"
              >
                <span className="font-bold text-[#0B3D2E] flex items-center gap-2 group-hover:text-[#2E7D32] transition-colors">
                  {item.title}
                  <ExternalLink size={14} className="opacity-0 group-hover:opacity-100 transition-opacity text-[#0B3D2E]" />
                </span>
                <span className="text-sm text-[#0B3D2E]/70 line-clamp-2 mt-1">{item.summary}</span>
              </a>
            ))}
          </div>
        </div>
      )}

      <div className="mt-12 relative z-10">
        <h2 className="text-2xl font-bold text-[#0B3D2E] mb-6 border-b border-[#0B3D2E]/10 pb-3">My submissions</h2>
        {loadingSubmissions ? (
          <div className="flex justify-center py-10 text-[#0B3D2E]/40">
            <Loader2 size={24} className="animate-spin" />
          </div>
        ) : submissions.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-[#0B3D2E]/20 bg-white/50 p-10 text-center">
            <p className="text-[#0B3D2E]/60 text-lg">Nothing submitted yet.</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {submissions.map((sub) => (
              <div key={sub.id} className="rounded-2xl border border-[#0B3D2E]/10 bg-white p-5 hover:border-[#0B3D2E]/30 transition-colors shadow-sm hover:shadow-md">
                <p className="font-bold text-lg text-[#0B3D2E]">{sub.title}</p>
                <p className="mt-2 text-sm text-[#0B3D2E]/80 line-clamp-2">{sub.abstract}</p>
                <div className="mt-4 flex flex-wrap gap-2 text-xs text-[#0B3D2E]/60 font-medium bg-[#0B3D2E]/5 rounded-lg p-2 px-3 inline-flex">
                  <span>{new Date(sub.created_at).toLocaleDateString()}</span>
                  {sub.species && (
                    <>
                      <span className="opacity-40">•</span>
                      <span>{sub.species}</span>
                    </>
                  )}
                  {sub.location && (
                    <>
                      <span className="opacity-40">•</span>
                      <span>{sub.location}</span>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Publications
