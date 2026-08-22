import { useEffect, useState } from "react"
import { AnimatePresence, motion } from "motion/react"

function App() {
  const [showSplash, setShowSplash] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowSplash(false)
    }, 2500)

    return () => clearTimeout(timer)
  }, [])

  return (
    <AnimatePresence mode="wait">
      {showSplash ? (
        <motion.main
          key="splash"
          className="fixed inset-0 flex items-center justify-center bg-[#0B3D2E]"
          initial={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.7, ease: "easeInOut" }}
        >
          <motion.img
            src="/jeevsetu-logo.png"
            alt="JeevSetu"
            className="w-[280px] sm:w-[360px] md:w-[440px] object-contain"
            initial={{ opacity: 0, scale: 0.92 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{
              duration: 1.2,
              ease: [0.22, 1, 0.36, 1],
            }}
          />
        </motion.main>
      ) : (
        <motion.main
          key="app"
          className="min-h-screen bg-[#F8F6E9] text-[#0B3D2E]"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6 }}
        >
          {/* Main application will be built here */}
          <div className="flex min-h-screen items-center justify-center">
            <h1 className="text-3xl font-semibold">
              JeevSetu
            </h1>
          </div>
        </motion.main>
      )}
    </AnimatePresence>
  )
}

export default App