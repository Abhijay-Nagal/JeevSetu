import { useEffect, useState, useMemo } from "react"
import { api } from "../lib/api"
import CommunityCard from "../components/community/CommunityCard"
import CommunityDetail from "../components/community/CommunityDetail"
import { Button } from "../components/ui/button"
import { Input } from "../components/ui/input"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../components/ui/dialog"
import { Search, Plus } from "lucide-react"
import AnimatedList from "../components/ui/AnimatedList"
import ShinyText from "../components/ui/ShinyText"

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
  const [searchQuery, setSearchQuery] = useState("")
  const [isDialogOpen, setIsDialogOpen] = useState(false)

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
      setIsDialogOpen(false)
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

  const filteredCommunities = useMemo(() => {
    const unjoined = communities.filter(c => !myCommunityIds.has(c.id))
    if (!searchQuery.trim()) return unjoined
    const lowerQuery = searchQuery.toLowerCase()
    return unjoined.filter((c) => c.name.toLowerCase().includes(lowerQuery))
  }, [communities, myCommunityIds, searchQuery])

  if (selected) {
    return <CommunityDetail community={selected} onBack={() => setSelected(null)} />
  }

  return (
    <div className="max-w-3xl space-y-8 p-8 rounded-3xl relative z-10 bg-white/70 backdrop-blur-xl border border-[#0B3D2E]/10 shadow-lg">
      
      <div className="flex items-center justify-between relative z-10">
        <div>
          <h1 className="text-4xl font-bold tracking-tight">
            <ShinyText text="Explore Communities" variant="green" />
          </h1>
          <p className="mt-3 text-lg opacity-80 text-[#0B3D2E]">Discover communities, or start your own.</p>
        </div>
      </div>

      <div className="flex items-center gap-4 relative z-10">
        <div className="relative flex-1 group">
          <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground transition-colors group-focus-within:text-[#0B3D2E]" />
          <Input 
            placeholder="Search communities..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-11 h-12 text-lg shadow-sm border-[#0B3D2E]/20 focus-visible:ring-[#0B3D2E] rounded-xl"
          />
        </div>
        
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger className="inline-flex h-12 items-center justify-center rounded-xl bg-[#0B3D2E] px-6 text-sm font-medium text-white shadow-md transition-all hover:bg-[#0B3D2E]/90 hover:shadow-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50">
            <Plus className="mr-2 h-5 w-5" />
            Create
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Start a community</DialogTitle>
              <DialogDescription>
                Create a new community to gather people around a shared interest.
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleCreateCommunity} className="space-y-4 pt-4">
              <div className="space-y-2">
                <Input
                  type="text"
                  placeholder="Name"
                  value={newName}
                  onChange={(event) => setNewName(event.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Input
                  type="text"
                  placeholder="Description (optional)"
                  value={newDescription}
                  onChange={(event) => setNewDescription(event.target.value)}
                />
              </div>
              {error && <p className="text-sm text-red-600">{error}</p>}
              <Button
                type="submit"
                disabled={creating}
                className="w-full bg-[#0B3D2E] hover:bg-[#0B3D2E]/90 text-white"
              >
                {creating ? "Creating..." : "Create community"}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {loading ? (
        <p className="opacity-60">Loading communities...</p>
      ) : filteredCommunities.length === 0 ? (
        <p className="opacity-60">No communities found.</p>
      ) : (
        <AnimatedList className="space-y-3 relative z-10" displayScrollbar={false}>
          {filteredCommunities.map((community) => (
            <CommunityCard
              key={community.id}
              community={community}
              isMember={myCommunityIds.has(community.id)}
              onOpen={setSelected}
              onJoin={handleJoin}
              onLeave={handleLeave}
            />
          ))}
        </AnimatedList>
      )}
    </div>
  )
}
