import { useEffect, useState } from "react";
import { api } from "../../lib/api";
import PostCard from "./PostCard";
import PostComposer from "./PostComposer";

export default function CommunityDetail({ community, onBack }) {
  const [posts, setPosts] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadFeed();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [community.slug]);

  async function loadFeed() {
    setError(null);
    try {
      const feed = await api.getCommunityFeed(community.slug);
      setPosts(feed);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleJoin() {
    setError(null);
    try {
      await api.joinCommunity(community.slug);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleLeave() {
    setError(null);
    try {
      await api.leaveCommunity(community.slug);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="max-w-2xl space-y-6">
      <button onClick={onBack} className="text-sm underline">
        &larr; Back
      </button>

      <div>
        <h1 className="text-2xl font-bold">{community.name}</h1>
        {community.description && <p className="mt-1 opacity-70">{community.description}</p>}
        <div className="mt-3 flex gap-2">
          <button onClick={handleJoin} className="rounded-lg bg-[#0B3D2E] px-3 py-1.5 text-sm text-white">
            Join
          </button>
          <button onClick={handleLeave} className="rounded-lg border border-[#0B3D2E]/20 px-3 py-1.5 text-sm">
            Leave
          </button>
        </div>
      </div>

      <PostComposer communitySlug={community.slug} onPosted={(post) => setPosts((prev) => [post, ...prev])} />

      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="space-y-4">
        {posts.length === 0 && <p className="opacity-60">No posts yet -- be the first.</p>}
        {posts.map((post) => (
          <PostCard key={post.id} post={post} />
        ))}
      </div>
    </div>
  );
}
