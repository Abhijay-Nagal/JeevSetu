import { useEffect, useState } from "react"
import { AnimatePresence, motion } from "motion/react"
import { createBrowserRouter, Navigate, RouterProvider } from "react-router-dom"
import { AuthProvider } from "./context/AuthContext"
import RequireAuth from "./components/RequireAuth"
import AppLayout from "./layouts/AppLayout"

// Every page under src/pages/*.jsx becomes a route automatically -- adding a
// page is just adding a file here, nobody edits a shared route list, so two
// people adding pages in parallel can't conflict.
//
// By default the path is derived from the filename (PascalCase -> kebab-case,
// "Home" -> "/"). A page only needs to export `route = { path: "..." }` when
// it wants something the filename can't express, e.g. a dynamic segment like
// "/communities/:slug/feed".
//
// A page opts into the sidebar shell (AppLayout) with `route.layout = "app"`
// -- those routes are nested under AppLayout and gated by RequireAuth.
// Everything else (Home, Login, Signup) renders standalone, full-page.
function deriveRouteFromFilename(filePath) {
  const name = filePath.replace("./pages/", "").replace(".jsx", "")
  if (name === "Home") return "/"
  const kebab = name.replace(/([a-z0-9])([A-Z])/g, "$1-$2").toLowerCase()
  return `/${kebab}`
}

const pageModules = import.meta.glob("./pages/*.jsx", { eager: true })
const appRoutes = []
const standaloneRoutes = []
for (const [filePath, module] of Object.entries(pageModules)) {
  const route = {
    path: module.route?.path ?? deriveRouteFromFilename(filePath),
    Component: module.default,
  }
  if (module.route?.layout === "app") {
    appRoutes.push(route)
  } else {
    standaloneRoutes.push(route)
  }
}

const router = createBrowserRouter([
  ...standaloneRoutes,
  {
    element: (
      <RequireAuth>
        <AppLayout />
      </RequireAuth>
    ),
    children: [
      ...appRoutes,
      // Catch-all: redirect any unknown route to home
      { path: "*", element: <Navigate to="/home" replace /> },
    ],
  },
  // Catch-all outside the app shell (unauthenticated unknown routes)
  { path: "*", element: <Navigate to="/" replace /> },
])

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
