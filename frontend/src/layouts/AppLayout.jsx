import { NavLink, Outlet } from "react-router-dom"
import { MessageCircle, Users, FileText } from "lucide-react"

const navigation = [
  {
    name: "Community",
    path: "/community",
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

        </div>
      </aside>

      <main className="ml-64 min-h-screen p-8">
        <Outlet />
      </main>
    </div>
  )
}

export default AppLayout