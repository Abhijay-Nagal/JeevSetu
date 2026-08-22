import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { supabase } from "../lib/supabaseClient";

export const route = { path: "/login" };

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);

    const { error: signInError } = await supabase.auth.signInWithPassword({ email, password });

    setSubmitting(false);

    if (signInError) {
      setError(signInError.message);
      return;
    }

    navigate("/explore-communities");
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#0B3D2E] text-[#F8F6E9] relative overflow-hidden">
      {/* Ambient backgrounds */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-[#F4C430]/10 rounded-full blur-[100px] -z-10 animate-pulse"></div>
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-[#2E7D32]/20 rounded-full blur-[100px] -z-10"></div>
      
      <form onSubmit={handleSubmit} className="w-full max-w-md space-y-5 p-8 bg-white/10 backdrop-blur-xl border border-white/10 rounded-3xl shadow-2xl relative z-10">
        <div className="flex justify-center mb-4">
          <Link to="/">
            <img src="/jeevsetu-logo.png" alt="JeevSetu" className="w-32 brightness-0 invert hover:opacity-80 transition" />
          </Link>
        </div>
        <h1 className="text-3xl font-bold text-center text-[#F4C430] mb-2">Welcome Back</h1>
        <p className="text-center text-sm opacity-80 mb-6">Log in to continue your journey</p>

        <div>
          <label htmlFor="email" className="block text-sm font-medium mb-1">
            Email
          </label>
          <input
            id="email"
            type="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="w-full rounded-xl border border-white/20 bg-white/5 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-[#F4C430] transition"
          />
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium mb-1">
            Password
          </label>
          <input
            id="password"
            type="password"
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="w-full rounded-xl border border-white/20 bg-white/5 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-[#F4C430] transition"
          />
        </div>

        {error && <p className="text-sm text-red-400 bg-red-400/10 p-3 rounded-lg text-center border border-red-400/20">{error}</p>}

        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-xl bg-[#F4C430] px-4 py-3 text-[#0B3D2E] font-bold text-lg hover:bg-[#F4C430]/90 transition shadow-lg disabled:opacity-50 mt-4"
        >
          {submitting ? "Logging in..." : "Log In"}
        </button>

        <p className="text-sm text-center pt-4 opacity-80">
          Need an account?{" "}
          <Link to="/signup" className="text-[#F4C430] font-semibold hover:underline">
            Sign up
          </Link>
        </p>
      </form>
    </div>
  );
}
