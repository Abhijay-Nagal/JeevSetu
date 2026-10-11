import { useEffect, useState } from "react"
import { ArrowLeft, Bird, Bug, Cat, Coins, Feather, Loader2, Lock, PawPrint, Shield, Squirrel, Turtle, Waves } from "lucide-react"
import { useNavigate } from "react-router-dom"
import SpotlightCard from "../components/ui/SpotlightCard"
import ShinyText from "../components/ui/ShinyText"
import SplitText from "../components/ui/SplitText"
import { api } from "../lib/api"
import { useWallet } from "../context/WalletContext"

export const route = { layout: "app" }

const ICONS = { bird: Bird, bug: Bug, cat: Cat, feather: Feather, "paw-print": PawPrint, shield: Shield, squirrel: Squirrel, turtle: Turtle, waves: Waves }

function CardArt({ card }) {
  if (card.image) {
    return <img src={card.image} alt={card.name} className="w-full h-full object-cover hover:scale-105 transition-transform duration-500" />
  }
  // Species without an illustration get a designed card face instead of a
  // broken image: the rarity colour, the animal's icon and its Latin name.
  const Icon = ICONS[card.icon] || PawPrint
  return (
    <div
      className="w-full h-full flex flex-col items-center justify-center gap-3 p-4 text-center"
      style={{ background: `radial-gradient(circle at 50% 35%, ${card.color}33, ${card.color}0d 70%), #F8F6E9` }}
    >
      <div className="rounded-full p-5 shadow-inner" style={{ backgroundColor: `${card.color}22`, color: card.color }}>
        <Icon size={56} strokeWidth={1.5} />
      </div>
      <p className="text-xs italic text-[#0B3D2E]/60">{card.scientific_name}</p>
    </div>
  )
}

function AnimalCard({ card }) {
  const [isFlipped, setIsFlipped] = useState(false)

  return (
    <div
      role="button"
      tabIndex={0}
      aria-pressed={isFlipped}
      aria-label={`${card.name} card -- ${isFlipped ? "showing details, activate to flip back" : "activate to flip for details"}`}
      className="relative w-full aspect-[3/4] cursor-pointer group [perspective:1000px] rounded-xl focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#F4C430] focus-visible:ring-offset-2"
      onClick={() => setIsFlipped(!isFlipped)}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault()
          setIsFlipped((flipped) => !flipped)
        }
      }}
    >
      <div
        className={`w-full h-full transition-all duration-700 [transform-style:preserve-3d] ${isFlipped ? '[transform:rotateY(180deg)]' : ''}`}
      >
        {/* Front */}
        <SpotlightCard spotlightColor={`${card.color}25`} className="absolute inset-0 p-4 bg-white flex flex-col hover:-translate-y-2 transition-transform duration-300 [backface-visibility:hidden]">
          <div className="flex-1 rounded-xl overflow-hidden bg-[#F8F6E9] mb-4 relative shadow-inner border-[3px]" style={{ borderColor: card.color }}>
            <CardArt card={card} />
            <div
              className="absolute bottom-0 left-0 right-0 py-2.5 px-4 text-center text-white font-bold text-sm tracking-[0.15em] uppercase backdrop-blur-md"
              style={{ backgroundColor: `${card.color}E6` }}
            >
              {card.rarity}
            </div>
          </div>
          <h3 className="font-bold text-xl text-center text-[#0B3D2E]">{card.name}</h3>
        </SpotlightCard>

        {/* Back */}
        <SpotlightCard spotlightColor={`${card.color}25`} className="absolute inset-0 bg-[#0B3D2E] text-[#F8F6E9] [backface-visibility:hidden] [transform:rotateY(180deg)] rounded-xl border-4" style={{ borderColor: card.color }}>
          <div className="flex flex-col w-full h-full p-6">
            {isFlipped ? (
              <>
                <h3 className="font-bold text-2xl text-center mb-1 shrink-0" style={{ color: card.color }}>
                  <SplitText text={card.name} />
                </h3>
                <p className="text-center text-xs italic opacity-70 mb-3">{card.scientific_name}</p>

                <div className="flex-1 flex flex-col px-1 overflow-y-auto min-h-0 pb-2">
                  <div className="my-auto">
                    <p className="mb-4 text-sm leading-snug opacity-90 text-center">
                      <SplitText text={card.description} delay={0.2} />
                    </p>

                    <div className="bg-white/10 p-3 mx-2 rounded-xl text-center">
                      <span className="font-bold text-xs uppercase opacity-70 block mb-1 tracking-wider" style={{ color: card.color }}>Habitat</span>
                      <span className="text-xs font-medium">{card.habitat}</span>
                    </div>
                    {card.iucn_status && (
                      <p className="mt-3 text-center text-xs opacity-80">IUCN: {card.iucn_status}</p>
                    )}
                  </div>
                </div>

                <div
                  className="mt-4 py-2 px-4 text-center text-white font-bold text-sm tracking-[0.15em] uppercase rounded-lg shrink-0"
                  style={{ backgroundColor: `${card.color}E6` }}
                >
                  {card.rarity}
                </div>
              </>
            ) : null}
          </div>
        </SpotlightCard>
      </div>
    </div>
  )
}

function LockedCard({ card, balance, busy, onCollect }) {
  const affordable = balance >= card.price
  return (
    <div className="relative w-full aspect-[3/4] rounded-xl border-2 border-dashed bg-white/70 p-4 flex flex-col" style={{ borderColor: `${card.color}66` }}>
      <div className="flex-1 rounded-xl overflow-hidden mb-4 relative grayscale opacity-50">
        <CardArt card={card} />
      </div>
      <div className="absolute top-6 right-6 rounded-full bg-[#0B3D2E]/80 p-2 text-white">
        <Lock size={14} />
      </div>
      <p className="text-xs font-bold uppercase tracking-widest text-center" style={{ color: card.color }}>{card.rarity}</p>
      <h3 className="font-bold text-lg text-center text-[#0B3D2E] mb-3">{card.name}</h3>
      <button
        onClick={() => onCollect(card)}
        disabled={!affordable || busy}
        className="flex items-center justify-center gap-2 rounded-xl bg-[#F4C430] px-4 py-2.5 text-sm font-bold text-[#0B3D2E] transition hover:bg-[#e0b422] disabled:bg-[#0B3D2E]/10 disabled:text-[#0B3D2E]/50 disabled:cursor-not-allowed"
      >
        {busy ? <Loader2 size={16} className="animate-spin" /> : <Coins size={16} />}
        {affordable ? `Collect for ${card.price}` : `Needs ${card.price} coins`}
      </button>
    </div>
  )
}

export default function Cards() {
  const navigate = useNavigate()
  const { refreshWallet } = useWallet()
  const [collection, setCollection] = useState(null)
  const [error, setError] = useState("")
  const [busyCard, setBusyCard] = useState(null)
  const [justCollected, setJustCollected] = useState("")

  useEffect(() => {
    api.getCards().then(setCollection).catch((err) => setError(err.message))
  }, [])

  async function handleCollect(card) {
    setBusyCard(card.id)
    setError("")
    try {
      setCollection(await api.collectCard(card.id))
      setJustCollected(card.name)
      refreshWallet()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusyCard(null)
    }
  }

  const owned = collection?.cards.filter((card) => card.owned) ?? []
  const locked = collection?.cards.filter((card) => !card.owned) ?? []

  return (
    <div className="max-w-5xl relative">
      <div className="absolute top-0 right-0 w-64 h-64 bg-[#F4C430]/10 rounded-full blur-3xl -z-10 animate-pulse"></div>

      <button
        onClick={() => navigate("/rewards")}
        className="flex items-center gap-2 text-sm font-medium text-[#0B3D2E]/70 hover:text-[#0B3D2E] transition mb-6"
      >
        <ArrowLeft size={16} />
        Back to Collectables
      </button>

      <div className="flex flex-wrap items-end justify-between gap-4 mb-8">
        <div>
          <h1 className="text-4xl font-bold tracking-tight mb-2">
            <ShinyText text="My Cards" variant="green" />
          </h1>
          <p className="opacity-70 max-w-2xl text-[#0B3D2E]">
            Spend the coins you earn -- answering daily questions, posting sightings and joining
            communities -- to collect cards of India's wildlife.
          </p>
        </div>
        {collection && (
          <div className="flex items-center gap-2 rounded-xl bg-[#0B3D2E] px-4 py-2.5 font-bold text-[#F8F6E9]">
            <Coins size={18} className="text-[#F4C430]" />
            {collection.coin_balance.toLocaleString()} coins
          </div>
        )}
      </div>

      {error && <div className="mb-6 rounded-xl border border-red-100 bg-red-50 p-4 text-red-700">{error}</div>}
      {justCollected && (
        <div role="status" className="mb-6 rounded-xl border border-[#81C784]/40 bg-[#81C784]/15 p-4 font-medium text-[#2E7D32]">
          {justCollected} added to your collection! Tap it to flip it over.
        </div>
      )}

      {!collection && !error && (
        <div className="flex justify-center py-16 text-[#0B3D2E]/40">
          <Loader2 size={24} className="animate-spin" />
        </div>
      )}

      {collection && (
        <>
          <h2 className="mb-4 text-lg font-bold">
            Collected <span className="text-[#0B3D2E]/50">({owned.length}/{collection.cards.length})</span>
          </h2>
          {owned.length === 0 ? (
            <p className="mb-10 rounded-xl border border-dashed border-[#0B3D2E]/20 bg-white/60 p-6 text-center text-[#0B3D2E]/60">
              No cards yet -- collect your first one below.
            </p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
              {owned.map((card) => (
                <AnimalCard key={card.id} card={card} />
              ))}
            </div>
          )}

          {locked.length > 0 && (
            <>
              <h2 className="mb-4 text-lg font-bold">Available to collect</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {locked.map((card) => (
                  <LockedCard
                    key={card.id}
                    card={card}
                    balance={collection.coin_balance}
                    busy={busyCard === card.id}
                    onCollect={handleCollect}
                  />
                ))}
              </div>
            </>
          )}
        </>
      )}
    </div>
  )
}
