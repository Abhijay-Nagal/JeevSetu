import { useEffect, useState, useMemo } from "react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog";
import { Search, Plus, Loader2 } from "lucide-react";
import { api } from "../../lib/api";
import PostCard from "./PostCard";
import PostComposer from "./PostComposer";

export default function CommunityDetail({ community, onBack, isMember, onJoin, onLeave }) {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [membershipBusy, setMembershipBusy] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const filteredPosts = useMemo(() => {
    if (!searchQuery.trim()) return posts;
    const lowerQuery = searchQuery.toLowerCase();
    return posts.filter(post =>
       post.description?.toLowerCase().includes(lowerQuery) ||
       post.species?.toLowerCase().includes(lowerQuery)
    );
  }, [posts, searchQuery]);

  useEffect(() => {
    loadFeed();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [community.slug]);

  async function loadFeed() {
    setError(null);
    setLoading(true);
    try {
      const feed = await api.getCommunityFeed(community.slug);
      setPosts(feed);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  // Both membership calls award or revoke coins, so block a second click
  // until the first one has come back.
  async function changeMembership(action) {
    if (membershipBusy || !action) return;
    setError(null);
    setMembershipBusy(true);
    try {
      await action(community);
    } catch (err) {
      setError(err.message);
    } finally {
      setMembershipBusy(false);
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
          {isMember ? (
            <button
              onClick={() => changeMembership(onLeave)}
              disabled={membershipBusy}
              className="rounded-lg border border-[#0B3D2E]/20 px-3 py-1.5 text-sm transition hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {membershipBusy ? "Leaving..." : "Leave"}
            </button>
          ) : (
            <button
              onClick={() => changeMembership(onJoin)}
              disabled={membershipBusy}
              className="rounded-lg bg-[#0B3D2E] px-3 py-1.5 text-sm text-white transition hover:bg-[#0B3D2E]/90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {membershipBusy ? "Joining..." : "Join"}
            </button>
          )}
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input 
            placeholder="Search posts..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        
        {isMember && (
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger render={<Button className="bg-[#0B3D2E] hover:bg-[#0B3D2E]/90 text-white" />}>
              <Plus className="mr-2 h-4 w-4" />
              Create post
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create a new post</DialogTitle>
                <DialogDescription>
                  Share something with {community.name}
                </DialogDescription>
              </DialogHeader>
              <div className="pt-4">
                <PostComposer
                  communitySlug={community.slug}
                  onPosted={(post) => {
                    setPosts((prev) => [post, ...prev]);
                    setIsDialogOpen(false);
                  }}
                />
              </div>
            </DialogContent>
          </Dialog>
        )}
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="space-y-4">
        {loading ? (
          <div className="flex justify-center py-8 text-[#0B3D2E]/40">
            <Loader2 size={20} className="animate-spin" />
          </div>
        ) : (
          filteredPosts.length === 0 && (
            <p className="opacity-60">
              {searchQuery.trim()
                ? `No posts match "${searchQuery.trim()}".`
                : isMember
                  ? "No posts yet -- share the first observation."
                  : "No posts yet. Join this community to start one."}
            </p>
          )
        )}
        {!loading &&
          filteredPosts.map((post) => <PostCard key={post.id} post={post} />)}
      </div>
    </div>
  );
}
