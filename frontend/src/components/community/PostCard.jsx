import { useState } from "react";
import { api } from "../../lib/api";

export default function PostCard({ post }) {
  const [likeCount, setLikeCount] = useState(post.like_count);
  const [liked, setLiked] = useState(false);
  const [busy, setBusy] = useState(false);

  async function toggleLike() {
    setBusy(true);
    try {
      const result = liked ? await api.unlikePost(post.id) : await api.likePost(post.id);
      setLikeCount(result.like_count);
      setLiked(result.liked_by_me);
    } finally {
      setBusy(false);
    }
  }

  return (
    <article className="rounded-xl border border-[#0B3D2E]/10 bg-white p-4">
      {post.media_url && (
        <img src={post.media_url} alt="" className="mb-3 max-h-80 w-full rounded-lg object-cover" />
      )}
      {post.species && <p className="text-sm font-semibold">{post.species}</p>}
      {post.description && <p className="mt-1 text-sm">{post.description}</p>}
      <div className="mt-3 flex items-center gap-2 text-sm">
        <button
          onClick={toggleLike}
          disabled={busy}
          className={`rounded-full px-3 py-1 transition ${
            liked ? "bg-[#F4C430] text-[#0B3D2E]" : "bg-[#0B3D2E]/5 hover:bg-[#0B3D2E]/10"
          }`}
        >
          {liked ? "Liked" : "Like"} ({likeCount})
        </button>
        {post.community_id === null && (
          <span className="rounded-full bg-[#0B3D2E]/5 px-2 py-1 text-xs opacity-70">Global</span>
        )}
      </div>
    </article>
  );
}
