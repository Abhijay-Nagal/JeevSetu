import { NavLink, Outlet } from "react-router-dom"
import { MessageCircle, Compass, Users, FileText, LogOut } from "lucide-react"
import { useAuth } from "../context/AuthContext"

const navigation = [
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
    name: "My Submissions",
    path: "/submissions",
    icon: FileText,
  },
]

function AppLayout() {
  const { user, signOut } = useAuth()

  return (
    <div className="min-h-screen bg-[#F8F6E9] text-[#0B3D2E]">
      <aside className="fixed inset-y-0 left-0 w-64 border-r border-[#0B3D2E]/10 bg-[#0B3D2E] text-[#F8F6E9]">
        <div className="flex h-full flex-col p-6">
          
          <div className="mb-10">
            <h1 className="text-2xl font-bold tracking-tight">
              JeevSetu
            </h1>
          </div>

          <nav className="space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon

              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition ${
                      isActive
                        ? "bg-[#F4C430] text-[#0B3D2E]"
                        : "text-[#F8F6E9]/75 hover:bg-white/10 hover:text-[#F8F6E9]"
                    }`
                  }
                >
                  <Icon size={19} />
                  {item.name}
                </NavLink>
              )
            })}
          </nav>

          <div className="mt-auto space-y-2 border-t border-white/10 pt-4">
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