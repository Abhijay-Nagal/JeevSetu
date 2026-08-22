import { useEffect, useState } from "react"
import { api } from "../lib/api"
import CommunityCard from "../components/community/CommunityCard"
import CommunityDetail from "../components/community/CommunityDetail"
import ShinyText from "../components/ui/ShinyText"
import AnimatedList from "../components/ui/AnimatedList"

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
    return (
      <CommunityDetail
        community={selected}
        onBack={() => setSelected(null)}
        isMember
        onLeave={async (community) => {
          await handleLeave(community)
          setSelected(null)
        }}
      />
    )
  }

  return (
    <div className="max-w-3xl space-y-8 p-6 rounded-2xl bg-gradient-to-br from-[#0B3D2E]/5 to-transparent relative overflow-hidden">
      <div className="absolute top-0 right-0 w-64 h-64 bg-[#F4C430]/10 rounded-full blur-3xl -z-10 animate-pulse"></div>
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-[#0B3D2E]/5 rounded-full blur-3xl -z-10"></div>

      <div>
        <h1 className="text-4xl font-bold tracking-tight">
          <ShinyText text="My Communities" />
        </h1>
        <p className="mt-3 text-lg opacity-80 text-[#0B3D2E]">Communities you've joined.</p>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {loading ? (
        <p className="opacity-60 text-[#0B3D2E]">Loading...</p>
      ) : communities.length === 0 ? (
        <p className="opacity-60 text-[#0B3D2E]">You haven't joined any communities yet -- find one under Explore.</p>
      ) : (
        <AnimatedList className="space-y-3 relative z-10" displayScrollbar={false}>
          {communities.map((community) => (
            <CommunityCard
              key={community.id}
              community={community}
              isMember
              onOpen={setSelected}
              onLeave={handleLeave}
            />
          ))}
        </AnimatedList>
      )}
    </div>
  )
}
