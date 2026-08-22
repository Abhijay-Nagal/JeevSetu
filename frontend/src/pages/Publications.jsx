import { useEffect, useState } from "react"
import { FlaskConical, Search, Loader2, ExternalLink } from "lucide-react"
import { api } from "../lib/api"
import { uploadObservationImage } from "../lib/storage"

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
    <div className="max-w-2xl">
      <h1 className="text-3xl font-semibold flex items-center gap-2">
        <FlaskConical size={26} className="text-[#2E7D32]" />
        Publications
      </h1>
      <p className="mt-2 opacity-70">
        Found something new? Submit your research to BNHS -- we'll check what's already known
        about it before you send it in.
      </p>

      <form onSubmit={handleSubmit} className="mt-8 space-y-4 rounded-2xl border border-[#0B3D2E]/10 bg-white p-6">
        <div>
          <label className="block text-sm font-medium mb-1">Title</label>
          <input
            type="text"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full rounded-lg border border-[#0B3D2E]/20 px-3 py-2 text-sm outline-none focus:border-[#F4C430]"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Abstract</label>
          <textarea
            required
            rows={4}
            value={abstract}
            onChange={(e) => setAbstract(e.target.value)}
            placeholder="Summarize your finding -- checked against BNHS's existing records when you submit."
            className="w-full resize-none rounded-lg border border-[#0B3D2E]/20 px-3 py-2 text-sm outline-none focus:border-[#F4C430]"
          />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium mb-1">Species (optional)</label>
            <input
              type="text"
              value={species}
              onChange={(e) => setSpecies(e.target.value)}
              className="w-full rounded-lg border border-[#0B3D2E]/20 px-3 py-2 text-sm outline-none focus:border-[#F4C430]"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Location (optional)</label>
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-full rounded-lg border border-[#0B3D2E]/20 px-3 py-2 text-sm outline-none focus:border-[#F4C430]"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Full write-up (optional)</label>
          <textarea
            rows={4}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full resize-none rounded-lg border border-[#0B3D2E]/20 px-3 py-2 text-sm outline-none focus:border-[#F4C430]"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Supporting document or image (optional)</label>
          <input
            type="file"
            accept="application/pdf,image/*"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            className="text-sm"
          />
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}
        {success && <p className="text-sm text-[#2E7D32]">Submitted -- BNHS will follow up on this.</p>}

        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-lg bg-[#0B3D2E] px-4 py-2.5 text-sm font-medium text-white disabled:opacity-50"
        >
          {submitting ? (
            <span className="flex items-center justify-center gap-2">
              <Loader2 size={15} className="animate-spin" />
              Checking BNHS records &amp; submitting...
            </span>
          ) : (
            "Submit to BNHS"
          )}
        </button>
      </form>

      {relatedResults && (
        <div className="mt-4 rounded-2xl border border-[#0B3D2E]/10 bg-white p-4 space-y-2">
          <p className="text-sm font-semibold flex items-center gap-1.5">
            <Search size={14} className="text-[#2E7D32]" />
            {relatedResults.length === 0 ? "No closely related BNHS records found" : "BNHS already has related records"}
          </p>
          {relatedResults.map((item, idx) => (
            <a
              key={idx}
              href={item.bnhs_url || "#"}
              target="_blank"
              rel="noreferrer"
              className="block rounded-md bg-[#F8F6E9] px-3 py-2 text-xs hover:border-[#F4C430] border border-transparent"
            >
              <span className="font-medium flex items-center gap-1">
                {item.title}
                <ExternalLink size={10} className="opacity-50" />
              </span>
              <span className="text-[#0B3D2E]/50 line-clamp-1">{item.summary}</span>
            </a>
          ))}
        </div>
      )}

      <h2 className="mt-8 mb-3 text-lg font-bold">My submissions</h2>
      {loadingSubmissions ? (
        <div className="flex justify-center py-6 text-[#0B3D2E]/40">
          <Loader2 size={18} className="animate-spin" />
        </div>
      ) : submissions.length === 0 ? (
        <p className="text-[#0B3D2E]/50 py-6 text-center">Nothing submitted yet.</p>
      ) : (
        <div className="space-y-2">
          {submissions.map((sub) => (
            <div key={sub.id} className="rounded-xl border border-[#0B3D2E]/10 bg-white p-4">
              <p className="font-semibold text-sm">{sub.title}</p>
              <p className="mt-1 text-sm text-[#0B3D2E]/70">{sub.abstract}</p>
              <p className="mt-2 text-xs text-[#0B3D2E]/40">
                {new Date(sub.created_at).toLocaleDateString()}
                {sub.species && ` · ${sub.species}`}
                {sub.location && ` · ${sub.location}`}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Publications
