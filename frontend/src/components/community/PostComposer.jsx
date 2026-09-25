import { useEffect, useState } from "react";
import { ImagePlus, X } from "lucide-react";
import { api } from "../../lib/api";
import { uploadObservationImage, validateObservationImage } from "../../lib/storage";
import { useWallet } from "../../context/WalletContext";

const MAX_DESCRIPTION = 1000;

export default function PostComposer({ communitySlug, onPosted }) {
  const { refreshWallet } = useWallet();
  const [description, setDescription] = useState("");
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  // Seeing the photo before it goes up catches the wrong-picture mistake that
  // otherwise only shows up once the post is already in the feed.
  useEffect(() => {
    if (!file) {
      setPreviewUrl(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  function handleFileChange(event) {
    const chosen = event.target.files?.[0] ?? null;
    const problem = validateObservationImage(chosen);
    if (problem) {
      setError(problem);
      event.target.value = "";
      return;
    }
    setError(null);
    setFile(chosen);
  }

  async function handleSubmit(event) {
    event.preventDefault();
    const trimmed = description.trim();
    if (!trimmed) {
      setError("Write something before posting.");
      return;
    }

    setError(null);
    setSubmitting(true);

    try {
      let mediaUrl = null;
      if (file) {
        mediaUrl = await uploadObservationImage(file);
      }

      const post = await api.createPost({
        description: trimmed,
        media_url: mediaUrl,
        community_slug: communitySlug,
      });

      setDescription("");
      setFile(null);
      onPosted(post);
      refreshWallet();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  const remaining = MAX_DESCRIPTION - description.length;

  return (
    <form onSubmit={handleSubmit} className="space-y-3 rounded-xl border border-[#0B3D2E]/10 bg-white p-4">
      <textarea
        placeholder="Share something with this community..."
        value={description}
        onChange={(event) => setDescription(event.target.value.slice(0, MAX_DESCRIPTION))}
        required
        rows={3}
        maxLength={MAX_DESCRIPTION}
        className="w-full resize-none rounded-lg border border-[#0B3D2E]/20 p-3 text-sm outline-none focus:border-[#F4C430]"
      />

      {previewUrl && (
        <div className="relative w-fit">
          <img
            src={previewUrl}
            alt="Selected observation preview"
            className="max-h-44 rounded-lg border border-[#0B3D2E]/10 object-cover"
          />
          <button
            type="button"
            onClick={() => setFile(null)}
            aria-label="Remove selected image"
            className="absolute -right-2 -top-2 rounded-full bg-[#0B3D2E] p-1 text-white shadow-md transition hover:bg-[#0B3D2E]/90"
          >
            <X size={14} />
          </button>
        </div>
      )}

      <div className="flex items-center justify-between gap-3">
        <label className="flex cursor-pointer items-center gap-2 rounded-lg border border-[#0B3D2E]/15 px-3 py-1.5 text-sm text-[#0B3D2E]/80 transition hover:border-[#F4C430] hover:text-[#0B3D2E]">
          <ImagePlus size={16} />
          {file ? "Change photo" : "Add photo"}
          <input type="file" accept="image/*" onChange={handleFileChange} className="sr-only" />
        </label>

        <div className="flex items-center gap-3">
          <span
            className={`text-xs tabular-nums ${remaining < 100 ? "text-[#0B3D2E]/70" : "text-[#0B3D2E]/40"}`}
          >
            {remaining}
          </span>
          <button
            type="submit"
            disabled={submitting || !description.trim()}
            className="rounded-lg bg-[#0B3D2E] px-4 py-2 text-sm font-medium text-white transition hover:bg-[#0B3D2E]/90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? "Posting..." : "Post"}
          </button>
        </div>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}
    </form>
  );
}
