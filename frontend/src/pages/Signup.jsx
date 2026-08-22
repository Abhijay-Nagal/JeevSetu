import { useState } from "react";
import { Link } from "react-router-dom";
import { supabase } from "../lib/supabaseClient";
import { api } from "../lib/api";

export const route = { path: "/signup" };

export default function Signup() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [confirmationSent, setConfirmationSent] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);

    const { data, error: signUpError } = await supabase.auth.signUp({
      email,
      password,
      options: { data: { name } },
    });

    setSubmitting(false);

    if (signUpError) {
      setError(signUpError.message);
      return;
    }

    // Fire-and-forget: our own branded confirmation email, independent of
    // whether Supabase already granted a session.
    api.sendConfirmationEmail(data.user.id, email, name).catch(() => {});

    // Our confirmation email is the intended gate, not Supabase's own
    // session state -- always show "check your email" so the user
    // actually goes and confirms, even though Supabase already granted a
    // session in the background (its own "Confirm email" requirement is
    // off, so signUp() returns a session either way).
    setConfirmationSent(true);
  }

  if (confirmationSent) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#F8F6E9] text-[#0B3D2E] px-4">
        <div className="max-w-sm text-center">
          <p>
            Check <strong>{email}</strong> for a confirmation link to finish signing up.
          </p>
          <Link to="/explore-communities" className="mt-6 inline-block text-sm underline">
            Continue to JeevSetu
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#0B3D2E] text-[#F8F6E9] relative overflow-hidden">
      {/* Ambient backgrounds */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-[#F4C430]/10 rounded-full blur-[100px] -z-10 animate-pulse"></div>
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-[#2E7D32]/20 rounded-full blur-[100px] -z-10"></div>
      
      <form onSubmit={handleSubmit} className="w-full max-w-md space-y-5 p-8 bg-white/10 backdrop-blur-xl border border-white/10 rounded-3xl shadow-2xl relative z-10 my-8">
        <div className="flex justify-center mb-4">
          <Link to="/">
            <img src="/jeevsetu-logo.png" alt="JeevSetu" className="w-32 brightness-0 invert hover:opacity-80 transition" />
          </Link>
        </div>
        <h1 className="text-3xl font-bold text-center text-[#F4C430] mb-2">Join JeevSetu</h1>
        <p className="text-center text-sm opacity-80 mb-6">Create an account to connect with wildlife</p>

        <div>
          <label htmlFor="name" className="block text-sm font-medium mb-1">
            Name
          </label>
          <input
            id="name"
            type="text"
            required
            value={name}
            onChange={(event) => setName(event.target.value)}
            className="w-full rounded-xl border border-white/20 bg-white/5 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-[#F4C430] transition"
          />
        </div>

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
            minLength={6}
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
          {submitting ? "Creating account..." : "Create Account"}
        </button>

        <p className="text-sm text-center pt-4 opacity-80">
          Already have an account?{" "}
          <Link to="/login" className="text-[#F4C430] font-semibold hover:underline">
            Log in
          </Link>
        </p>
      </form>
    </div>
  );
}
