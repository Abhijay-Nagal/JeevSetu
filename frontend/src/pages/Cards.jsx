import { useState } from "react"
import { ArrowLeft } from "lucide-react"
import { useNavigate } from "react-router-dom"
import SpotlightCard from "../components/ui/SpotlightCard"
import ShinyText from "../components/ui/ShinyText"
import SplitText from "../components/ui/SplitText"

export const route = { layout: "app" }

const myCards = [
  {
    id: "peacock",
    name: "Peacock",
    rarity: "Epic",
    color: "#9C27B0", // Purple for Epic
    image: "/cards/peacock.jpg",
    habitat: "Forests, agricultural lands, and urban areas in South Asia.",
    description: "The Indian peafowl, known for its magnificent tail feathers, is a large and brightly colored bird native to the Indian subcontinent."
  },
  {
    id: "beetle",
    name: "Rhino Beetle",
    rarity: "Rare",
    color: "#2196F3", // Blue for Rare
    image: "/cards/beetle.jpg",
    habitat: "Tropical rainforests and woodlands across the globe.",
    description: "Known for their immense strength and large horns, rhinoceros beetles are among the largest of beetles and can lift incredibly heavy objects."
  },
  {
    id: "monkey",
    name: "Jungle Monkey",
    rarity: "Common",
    color: "#4CAF50", // Green for Common
    image: "/cards/monkey.jpg",
    habitat: "Dense tropical rainforests and canopies.",
    description: "Agile and highly intelligent, these primates are known for their strong social bonds, curiosity, and incredible swinging abilities."
  }
]

function AnimalCard({ card }) {
  const [isFlipped, setIsFlipped] = useState(false)

  return (
    <div 
      className="relative w-full aspect-[3/4] cursor-pointer group [perspective:1000px]"
      onClick={() => setIsFlipped(!isFlipped)}
    >
      <div 
        className={`w-full h-full transition-all duration-700 [transform-style:preserve-3d] ${isFlipped ? '[transform:rotateY(180deg)]' : ''}`}
      >
        {/* Front */}
        <SpotlightCard spotlightColor={`${card.color}25`} className="absolute inset-0 p-4 bg-white flex flex-col hover:-translate-y-2 transition-transform duration-300 [backface-visibility:hidden]">
          <div className="flex-1 rounded-xl overflow-hidden bg-[#F8F6E9] mb-4 relative shadow-inner border-[3px]" style={{ borderColor: card.color }}>
            <img src={card.image} alt={card.name} className="w-full h-full object-cover hover:scale-105 transition-transform duration-500" />
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
                <h3 className="font-bold text-2xl text-center mb-4 shrink-0" style={{ color: card.color }}>
                  <SplitText text={card.name} />
                </h3>
                
                <div className="flex-1 flex flex-col px-1 overflow-y-auto min-h-0 pb-2">
                  <div className="my-auto">
                    <p className="mb-4 text-sm leading-snug opacity-90 text-center">
                      <SplitText text={card.description} delay={0.2} />
                    </p>
                    
                    <div className="bg-white/10 p-3 mx-2 rounded-xl text-center">
                      <span className="font-bold text-xs uppercase opacity-70 block mb-1 tracking-wider" style={{ color: card.color }}>Habitat</span>
                      <span className="text-xs font-medium">{card.habitat}</span>
                    </div>
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

export default function Cards() {
  const navigate = useNavigate()

  return (
    <div className="max-w-4xl relative">
      <div className="absolute top-0 right-0 w-64 h-64 bg-[#F4C430]/10 rounded-full blur-3xl -z-10 animate-pulse"></div>

      <button 
        onClick={() => navigate("/rewards")}
        className="flex items-center gap-2 text-sm font-medium text-[#0B3D2E]/70 hover:text-[#0B3D2E] transition mb-6"
      >
        <ArrowLeft size={16} />
        Back to Collectables
      </button>

      <h1 className="text-4xl font-bold tracking-tight mb-2">
        <ShinyText text="My Cards" variant="green" />
      </h1>
      <p className="opacity-70 mb-8 max-w-2xl text-[#0B3D2E]">
        Your collection of animal trading cards. Keep participating in communities to earn more coins and unlock new cards!
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {myCards.map((card) => (
          <AnimalCard key={card.id} card={card} />
        ))}
      </div>
    </div>
  )
}
