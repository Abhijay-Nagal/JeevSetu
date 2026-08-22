import { useEffect, useState } from "react"
import { AnimatePresence, motion } from "motion/react"
import { createBrowserRouter, RouterProvider } from "react-router-dom"
import { AuthProvider } from "./context/AuthContext"

// Every page under src/pages/*.jsx exports `route` (its path) and a default
// component. Adding a page is just adding a file here -- nobody edits this
// list, so two people adding routes in parallel can't conflict.
const pageModules = import.meta.glob("./pages/*.jsx", { eager: true })
const routes = Object.values(pageModules).map((module) => ({
  path: module.route.path,
  Component: module.default,
}))
const router = createBrowserRouter(routes)

function App() {
  const [showSplash, setShowSplash] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowSplash(false)
    }, 2500)

    return () => clearTimeout(timer)
  }, [])

  return (
    <AuthProvider>
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
          <motion.div
            key="app"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6 }}
          >
            <RouterProvider router={router} />
          </motion.div>
        )}
      </AnimatePresence>
    </AuthProvider>
  )
}

export default App
