import { NavLink, Outlet } from "react-router-dom"
import { Home as HomeIcon, MessageCircle, Compass, Users, FileText, LogOut, Coins, FlaskConical } from "lucide-react"
import { useAuth } from "../context/AuthContext"
import { useWallet } from "../context/WalletContext"
import SpotlightCard from "../components/ui/SpotlightCard"

const navigation = [
  {
    name: "Home",
    path: "/home",
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
    name: "Chatbot",
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
]

function AppLayout() {
  const { user, signOut } = useAuth()
  const { wallet } = useWallet()
  const coinBalance = wallet?.coin_balance ?? null

  return (
    <div className="min-h-screen bg-[#F8F6E9] text-[#0B3D2E]">
      <aside className="fixed inset-y-0 left-0 w-64 border-r border-[#0B3D2E]/10 bg-[#0B3D2E] text-[#F8F6E9]">
        <div className="flex h-full flex-col p-6 overflow-y-auto">

          <div className="mb-6 flex flex-col items-center shrink-0">
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
              className="flex items-center justify-center gap-2 rounded-xl bg-[#F4C430] px-4 py-2.5 text-sm font-bold text-[#0B3D2E] transition hover:bg-[#e0b422] relative z-10 w-full h-full"
            >
              <Coins size={16} />
              My Collectables
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
            <p className="truncate px-4 text-xs text-[#F8F6E9]/60">
              {user?.user_metadata?.name || user?.email}
            </p>
            <button
              onClick={signOut}
              className="flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-[#F8F6E9]/75 transition hover:bg-white/10 hover:text-[#F8F6E9]"
            >
              <LogOut size={19} />
              Sign out
            </button>
          </div>

        </div>
      </aside>

      <main className="ml-64 min-h-screen p-8">
        <Outlet />
      </main>
    </div>
  )
}

export default AppLayout