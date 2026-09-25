// The collectable card set lives here rather than inside Cards.jsx so the
// Rewards page can show a real "My Cards" count instead of a hardcoded one --
// adding a card to this list updates both screens.
export const myCards = [
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
