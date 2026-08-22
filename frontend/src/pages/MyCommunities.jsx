import { useEffect, useState } from "react"
import { api } from "../lib/api"
import CommunityCard from "../components/community/CommunityCard"
import CommunityDetail from "../components/community/CommunityDetail"

export const route = { layout: "app" }

export default function MyCommunities() {
  const [communities, setCommunities] = useState([])
  const [selected, setSelected] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const mine = await api.myCommunities()
      setCommunities(mine)
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

  async function handleLeave(community) {
    setError(null)
    try {
      await api.leaveCommunity(community.slug)
      setCommunities((prev) => prev.filter((c) => c.id !== community.id))
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
        <h1 className="text-3xl font-semibold">My Communities</h1>
        <p className="mt-2 opacity-70">Communities you've joined.</p>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {loading ? (
        <p className="opacity-60">Loading...</p>
      ) : communities.length === 0 ? (
        <p className="opacity-60">You haven't joined any communities yet -- find one under Explore.</p>
      ) : (
        <div className="space-y-3">
          {communities.map((community) => (
            <CommunityCard
              key={community.id}
              community={community}
              isMember
              onOpen={setSelected}
              onLeave={handleLeave}
            />
          ))}
        </div>
      )}
    </div>
  )
}
