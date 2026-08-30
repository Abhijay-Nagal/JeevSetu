import { useLocation, Link } from "react-router-dom"
import { useAuth } from "../context/AuthContext"
import { Lock } from "lucide-react"

export default function RequireAuth({ children }) {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) return null

  if (!user) {
    return (
      <div className="flex flex-col items-center justify-center h-full min-h-[60vh] text-center px-4">
        <div className="bg-[#0B3D2E] text-[#F8F6E9] p-8 rounded-2xl shadow-xl max-w-md w-full border border-white/10 flex flex-col items-center">
          <div className="bg-[#F4C430]/20 p-4 rounded-full mb-6">
            <Lock size={48} className="text-[#F4C430]" />
          </div>
          <h2 className="text-2xl font-bold mb-4">Login to Continue</h2>
          <p className="text-[#F8F6E9]/80 mb-8 leading-relaxed">
            Please log in or create an account to access this section and join our community.
          </p>
          <div className="flex flex-col w-full gap-3">
            <Link 
              to="/login" 
              state={{ from: location }} 
              className="w-full bg-[#F4C430] text-[#0B3D2E] font-bold py-3 rounded-xl hover:bg-[#e0b422] transition"
            >
              Log In
            </Link>
            <Link 
              to="/signup" 
              className="w-full bg-transparent border border-[#F4C430] text-[#F4C430] font-bold py-3 rounded-xl hover:bg-[#F4C430]/10 transition"
            >
              Create Account
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return children
}
