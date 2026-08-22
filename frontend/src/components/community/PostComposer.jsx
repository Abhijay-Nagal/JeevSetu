import { useState } from "react";
import { api } from "../../lib/api";
import { uploadObservationImage } from "../../lib/storage";

export default function PostComposer({ communitySlug, onPosted }) {
  const [description, setDescription] = useState("");
  const [file, setFile] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      let mediaUrl = null;
      if (file) {
        mediaUrl = await uploadObservationImage(file);
      }

      const post = await api.createPost({
        description,
        media_url: mediaUrl,
        community_slug: communitySlug,
      });

      setDescription("");
      setFile(null);
      onPosted(post);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3 rounded-xl border border-[#0B3D2E]/10 bg-white p-4">
      <textarea
        placeholder="Share something with this community..."
        value={description}
        onChange={(event) => setDescription(event.target.value)}
        required
        rows={3}
        className="w-full resize-none rounded-lg border border-[#0B3D2E]/20 p-3 text-sm"
      />
      <div className="flex items-center justify-between">
        <input
          type="file"
          accept="image/*"
          onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          className="text-sm"
        />
        <button
          type="submit"
          disabled={submitting}
          className="rounded-lg bg-[#0B3D2E] px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {submitting ? "Posting..." : "Post"}
        </button>
      </div>
      {error && <p className="text-sm text-red-600">{error}</p>}
    </form>
  );
}
