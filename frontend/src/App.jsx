import { useEffect, useState } from "react"
import { AnimatePresence, motion } from "motion/react"
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom"

import AppLayout from "./layouts/AppLayout"
import Community from "./pages/Community"
import Chatbot from "./pages/Chatbot"
import MySubmissions from "./pages/MySubmissions"

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
          className="min-h-screen"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6 }}
        >
          <BrowserRouter>
            <Routes>
              <Route element={<AppLayout />}>
                <Route
                  index
                  element={<Navigate to="/community" replace />}
                />

                <Route
                  path="/community"
                  element={<Community />}
                />

                <Route
                  path="/chatbot"
                  element={<Chatbot />}
                />

                <Route
                  path="/submissions"
                  element={<MySubmissions />}
                />
              </Route>
            </Routes>
          </BrowserRouter>
        </motion.main>
      )}
    </AnimatePresence>
  )
}

export default App