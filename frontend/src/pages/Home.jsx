import { Link, Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export const route = { path: "/" };

export default function Home() {
  const { user, loading } = useAuth();

  if (loading) return null;
  if (user) return <Navigate to="/explore-communities" replace />;

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-[#F8F6E9] text-[#0B3D2E]">
      <h1 className="text-3xl font-semibold">JeevSetu</h1>
      <div className="flex gap-4">
        <Link to="/login" className="underline">
          Log in
        </Link>
        <Link to="/signup" className="underline">
          Sign up
        </Link>
      </div>
    </div>
  );
}
