import { useState } from "react";
import { MessageCircle, Loader2 } from "lucide-react";
import { api } from "../../lib/api";

export default function PostCard({ post }) {
  const [likeCount, setLikeCount] = useState(post.like_count);
  const [liked, setLiked] = useState(post.liked_by_me || false);
  const [busy, setBusy] = useState(false);

  const [showComments, setShowComments] = useState(false);
  const [comments, setComments] = useState(null);
  const [loadingComments, setLoadingComments] = useState(false);
  const [newComment, setNewComment] = useState("");
  const [submittingComment, setSubmittingComment] = useState(false);
  const [commentError, setCommentError] = useState("");

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

  async function toggleComments() {
    const next = !showComments;
    setShowComments(next);
    if (next && comments === null) {
      setLoadingComments(true);
      try {
        setComments(await api.listComments(post.id));
      } catch (err) {
        setCommentError(err.message);
      } finally {
        setLoadingComments(false);
      }
    }
  }

  async function handleAddComment(event) {
    event.preventDefault();
    if (!newComment.trim()) return;
    setSubmittingComment(true);
    setCommentError("");
    try {
      const comment = await api.addComment(post.id, newComment.trim());
      setComments((prev) => [...(prev || []), comment]);
      setNewComment("");
    } catch (err) {
      setCommentError(err.message);
    } finally {
      setSubmittingComment(false);
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
        <button
          onClick={toggleComments}
          className="flex items-center gap-1 rounded-full bg-[#0B3D2E]/5 px-3 py-1 hover:bg-[#0B3D2E]/10"
        >
          <MessageCircle size={14} />
          {comments === null ? "Comments" : `Comments (${comments.length})`}
        </button>
        {post.community_id === null && (
          <span className="rounded-full bg-[#0B3D2E]/5 px-2 py-1 text-xs opacity-70">Global</span>
        )}
      </div>

      {showComments && (
        <div className="mt-3 border-t border-[#0B3D2E]/10 pt-3 space-y-3">
          {loadingComments ? (
            <div className="flex justify-center py-3 text-[#0B3D2E]/40">
              <Loader2 size={16} className="animate-spin" />
            </div>
          ) : (
            <>
              {comments?.length === 0 && (
                <p className="text-xs text-[#0B3D2E]/50">
                  No comments yet -- be the first to add what you know.
                </p>
              )}
              {comments?.map((comment) => (
                <div key={comment.id} className="text-sm">
                  <span className="font-semibold">{comment.user_name || "Someone"}</span>{" "}
                  <span className="text-[#0B3D2E]/50 text-xs">
                    {new Date(comment.created_at).toLocaleDateString()}
                  </span>
                  <p className="text-[#0B3D2E]/80">{comment.content}</p>
                </div>
              ))}
            </>
          )}

          <form onSubmit={handleAddComment} className="flex gap-2">
            <input
              type="text"
              value={newComment}
              onChange={(event) => setNewComment(event.target.value)}
              placeholder="Add what you know..."
              className="flex-1 rounded-lg border border-[#0B3D2E]/15 px-3 py-1.5 text-sm outline-none focus:border-[#F4C430]"
            />
            <button
              type="submit"
              disabled={submittingComment || !newComment.trim()}
              className="rounded-lg bg-[#0B3D2E] px-3 py-1.5 text-sm text-white disabled:opacity-50"
            >
              Post
            </button>
          </form>
          {commentError && <p className="text-xs text-red-600">{commentError}</p>}
        </div>
      )}
    </article>
  );
}
