import { NavLink, Outlet } from "react-router-dom"
import { useEffect, useState } from "react"
import { Home as HomeIcon, MessageCircle, Compass, Users, FileText, LogOut, Coins, FlaskConical, Bell, Menu, X } from "lucide-react"
import { useAuth } from "../context/AuthContext"
import { useWallet } from "../context/WalletContext"
import SpotlightCard from "../components/ui/SpotlightCard"
import Particles from "../components/ui/Particles"

const navigation = [
  {
    name: "Home",
    path: "/",
    icon: HomeIcon,
  },
  {
    name: "Explore Communities",
    path: "/explore-communities",
    icon: Compass,
  },
  {
    name: "My Communities",
    path: "/my-communities",
    icon: Users,
  },
  {
    name: "Knowledge Hub",
    path: "/chatbot",
    icon: MessageCircle,
  },
  {
    name: "Publications",
    path: "/publications",
    icon: FlaskConical,
  },
  {
    name: "My Submissions",
    path: "/submissions",
    icon: FileText,
  },
  {
    name: "Notifications",
    path: "/notifications",
    icon: Bell,
  },
]

function AppLayout() {
  const { user, signOut } = useAuth()
  const { wallet } = useWallet()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const coinBalance = wallet?.coin_balance ?? null

  const handleNavClick = () => setIsMobileMenuOpen(false)

  // While the drawer is open it owns the screen: Escape closes it, and the
  // page behind it stops scrolling so a swipe doesn't drag the feed around
  // underneath the overlay.
  useEffect(() => {
    if (!isMobileMenuOpen) return

    const handleKeyDown = (event) => {
      if (event.key === "Escape") setIsMobileMenuOpen(false)
    }

    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = "hidden"
    window.addEventListener("keydown", handleKeyDown)

    return () => {
      document.body.style.overflow = previousOverflow
      window.removeEventListener("keydown", handleKeyDown)
    }
  }, [isMobileMenuOpen])

  return (
    <div className="min-h-screen bg-[#F8F6E9] text-[#0B3D2E] relative flex flex-col md:flex-row">
      <div className="fixed inset-0 z-0 pointer-events-none opacity-40">
        <Particles 
          particleCount={80}
          speed={0.8}
          particleColor="#0B3D2E"
          lineColor="#0B3D2E"
        />
      </div>

      {/* Mobile Header */}
      <div className="md:hidden flex items-center justify-between bg-[#0B3D2E] text-[#F8F6E9] h-16 px-4 z-40 fixed top-0 w-full shadow-md">
         <span className="font-serif font-bold text-2xl tracking-wide ml-2">
           <span className="text-white">Jeev</span><span className="text-[#6ab457]">Setu</span>
         </span>
         <button
           onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
           className="p-1 rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#F4C430]"
           aria-label={isMobileMenuOpen ? "Close navigation menu" : "Open navigation menu"}
           aria-expanded={isMobileMenuOpen}
           aria-controls="app-sidebar"
         >
           {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
         </button>
      </div>

      {/* Mobile Overlay */}
      <div 
        className={`fixed inset-0 bg-black/50 z-40 md:hidden transition-opacity duration-300 ${isMobileMenuOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`} 
        onClick={() => setIsMobileMenuOpen(false)} 
        aria-hidden="true"
      />

      <aside id="app-sidebar" aria-label="Main navigation" className={`fixed inset-y-0 left-0 w-64 border-r border-[#0B3D2E]/10 bg-[#0B3D2E] text-[#F8F6E9] z-50 transform transition-transform duration-300 md:translate-x-0 ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="flex h-full flex-col p-6 overflow-y-auto">

          <div className="mb-6 flex flex-col items-center shrink-0 pt-8 md:pt-0">
            <img src="/jeevsetu-logo.png" alt="JeevSetu Logo" className="mb-2 w-48 h-auto" />
            <h1 className="sr-only">
              JeevSetu
            </h1>
          </div>

          <SpotlightCard
            spotlightColor="rgba(255, 255, 255, 0.4)"
            className="mb-6 p-0 border-none bg-transparent hover:translate-y-0 shadow-none hover:shadow-none rounded-xl shrink-0 block"
          >
            <NavLink
              to="/rewards"
              onClick={handleNavClick}
              className="flex items-center justify-center gap-2 rounded-xl bg-[#F4C430] px-4 py-2.5 text-sm font-bold text-[#0B3D2E] transition hover:bg-[#e0b422] relative z-10 w-full h-full"
            >
              <Coins size={16} />
              My Collectables
              {coinBalance !== null && (
                <span className="rounded-full bg-[#0B3D2E]/15 px-2 py-0.5 text-xs font-bold tabular-nums">
                  {coinBalance.toLocaleString()}
                </span>
              )}
            </NavLink>
          </SpotlightCard>

          <nav className="space-y-2 shrink-0">
            {navigation.map((item) => {
              const Icon = item.icon

              return (
                <SpotlightCard
                  key={item.path}
                  spotlightColor="rgba(244, 196, 48, 0.15)"
                  className="p-0 border-none bg-transparent hover:translate-y-0 shadow-none hover:shadow-none shrink-0 block"
                >
                  <NavLink
                    to={item.path}
                    onClick={handleNavClick}
                    className={({ isActive }) =>
                      `flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition relative z-10 w-full h-full ${
                        isActive
                          ? "bg-[#F4C430] text-[#0B3D2E]"
                          : "text-[#F8F6E9]/75 hover:bg-white/10 hover:text-[#F8F6E9]"
                      }`
                    }
                  >
                    <Icon size={19} />
                    {item.name}
                  </NavLink>
                </SpotlightCard>
              )
            })}
          </nav>

          <div className="mt-auto space-y-2 border-t border-white/10 pt-4 shrink-0 pb-4">
            {user ? (
              <>
                <p className="truncate px-4 text-xs text-[#F8F6E9]/60">
                  {user?.user_metadata?.name || user?.email}
                </p>
                <button
                  onClick={() => { signOut(); handleNavClick(); }}
                  className="flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-[#F8F6E9]/75 transition hover:bg-white/10 hover:text-[#F8F6E9]"
                >
                  <LogOut size={19} />
                  Sign out
                </button>
              </>
            ) : (
              <div className="flex flex-col gap-2 px-4">
                <NavLink
                  to="/login"
                  onClick={handleNavClick}
                  className="flex w-full items-center justify-center gap-2 rounded-xl bg-[#F4C430] px-4 py-2.5 text-sm font-bold text-[#0B3D2E] transition hover:bg-[#e0b422]"
                >
                  Log In
                </NavLink>
                <NavLink
                  to="/signup"
                  onClick={handleNavClick}
                  className="flex w-full items-center justify-center gap-2 rounded-xl border border-[#F4C430] px-4 py-2.5 text-sm font-bold text-[#F4C430] transition hover:bg-[#F4C430]/10"
                >
                  Sign Up
                </NavLink>
              </div>
            )}
          </div>

        </div>
      </aside>

      <main className="flex-1 md:ml-64 min-h-screen p-4 pt-20 md:p-8 relative z-10 w-full overflow-hidden">
        <Outlet />
      </main>
    </div>
  )
}

export default AppLayout