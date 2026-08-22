import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { supabase } from "../lib/supabaseClient";

export const route = { path: "/signup" };

export default function Signup() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [confirmationSent, setConfirmationSent] = useState(false);
  const navigate = useNavigate();

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

    if (data.session) {
      navigate("/");
    } else {
      // Email confirmation is required before a session exists.
      setConfirmationSent(true);
    }
  }

  if (confirmationSent) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#F8F6E9] text-[#0B3D2E]">
        <p className="max-w-sm text-center">
          Check <strong>{email}</strong> for a confirmation link to finish signing up.
        </p>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#F8F6E9] text-[#0B3D2E]">
      <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-4 p-6">
        <h1 className="text-2xl font-semibold">Sign up</h1>

        <div>
          <label htmlFor="name" className="block text-sm font-medium">
            Name
          </label>
          <input
            id="name"
            type="text"
            required
            value={name}
            onChange={(event) => setName(event.target.value)}
            className="mt-1 w-full rounded border border-[#0B3D2E]/30 px-3 py-2"
          />
        </div>

        <div>
          <label htmlFor="email" className="block text-sm font-medium">
            Email
          </label>
          <input
            id="email"
            type="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="mt-1 w-full rounded border border-[#0B3D2E]/30 px-3 py-2"
          />
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium">
            Password
          </label>
          <input
            id="password"
            type="password"
            required
            minLength={6}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="mt-1 w-full rounded border border-[#0B3D2E]/30 px-3 py-2"
          />
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded bg-[#0B3D2E] px-4 py-2 text-white disabled:opacity-50"
        >
          {submitting ? "Creating account..." : "Create account"}
        </button>

        <p className="text-sm">
          Already have an account?{" "}
          <Link to="/login" className="underline">
            Log in
          </Link>
        </p>
      </form>
    </div>
  );
}
