import { useEffect, useState } from "react"
import { api } from "../lib/api"
import CommunityCard from "../components/community/CommunityCard"
import CommunityDetail from "../components/community/CommunityDetail"

export const route = { layout: "app" }

export default function ExploreCommunities() {
  const [communities, setCommunities] = useState([])
  const [myCommunityIds, setMyCommunityIds] = useState(new Set())
  const [selected, setSelected] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [newName, setNewName] = useState("")
  const [newDescription, setNewDescription] = useState("")
  const [creating, setCreating] = useState(false)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const [all, mine] = await Promise.all([api.listCommunities(), api.myCommunities()])
      setCommunities(all)
      setMyCommunityIds(new Set(mine.map((community) => community.id)))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function handleCreateCommunity(event) {
    event.preventDefault()
    setCreating(true)
    setError(null)
    try {
      const community = await api.createCommunity({ name: newName, description: newDescription || null })
      setNewName("")
      setNewDescription("")
      setCommunities((prev) => [community, ...prev])
      setMyCommunityIds((prev) => new Set(prev).add(community.id))
    } catch (err) {
      setError(err.message)
    } finally {
      setCreating(false)
    }
  }

  async function handleJoin(community) {
    setError(null)
    try {
      await api.joinCommunity(community.slug)
      setMyCommunityIds((prev) => new Set(prev).add(community.id))
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleLeave(community) {
    setError(null)
    try {
      await api.leaveCommunity(community.slug)
      setMyCommunityIds((prev) => {
        const next = new Set(prev)
        next.delete(community.id)
        return next
      })
    } catch (err) {
      setError(err.message)
    }
  }

  if (selected) {
    return <CommunityDetail community={selected} onBack={() => setSelected(null)} />
  }

  return (
    <div className="max-w-2xl space-y-8">
      <div>
        <h1 className="text-3xl font-semibold">Explore Communities</h1>
        <p className="mt-2 opacity-70">Discover communities, or start your own.</p>
      </div>

      <form onSubmit={handleCreateCommunity} className="space-y-3 rounded-xl border border-[#0B3D2E]/10 bg-white p-4">
        <h2 className="font-semibold">Start a community</h2>
        <input
          type="text"
          placeholder="Name"
          value={newName}
          onChange={(event) => setNewName(event.target.value)}
          required
          className="w-full rounded-lg border border-[#0B3D2E]/20 p-2 text-sm"
        />
        <input
          type="text"
          placeholder="Description (optional)"
          value={newDescription}
          onChange={(event) => setNewDescription(event.target.value)}
          className="w-full rounded-lg border border-[#0B3D2E]/20 p-2 text-sm"
        />
        <button
          type="submit"
          disabled={creating}
          className="rounded-lg bg-[#0B3D2E] px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {creating ? "Creating..." : "Create community"}
        </button>
      </form>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {loading ? (
        <p className="opacity-60">Loading communities...</p>
      ) : communities.length === 0 ? (
        <p className="opacity-60">No communities yet -- create the first one above.</p>
      ) : (
        <div className="space-y-3">
          {communities.map((community) => (
            <CommunityCard
              key={community.id}
              community={community}
              isMember={myCommunityIds.has(community.id)}
              onOpen={setSelected}
              onJoin={handleJoin}
              onLeave={handleLeave}
            />
          ))}
        </div>
      )}
    </div>
  )
}
