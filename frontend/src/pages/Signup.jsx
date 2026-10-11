import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { CheckCircle2, Loader2, XCircle } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { api } from "../lib/api";

export const route = { path: "/signup" };

const USERNAME_PATTERN = /^[a-z][a-z0-9_.]{2,23}$/;
const USERNAME_HINT = "3-24 characters: lowercase letters, numbers, '_' or '.', starting with a letter.";

const inputClass =
  "w-full rounded-xl border border-white/20 bg-white/5 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-[#F4C430] transition";

function useUsernameAvailability(username) {
  // { state: "idle" | "invalid" | "checking" | "available" | "taken" | "error", message }
  const [result, setResult] = useState({ state: "idle", message: "" });

  useEffect(() => {
    if (!username) {
      setResult({ state: "idle", message: "" });
      return;
    }
    if (!USERNAME_PATTERN.test(username)) {
      setResult({ state: "invalid", message: USERNAME_HINT });
      return;
    }
    setResult({ state: "checking", message: "" });
    // Debounced so typing a name doesn't fire a request per keystroke.
    const timer = setTimeout(() => {
      api
        .checkUsername(username)
        .then((data) =>
          setResult(
            data.available
              ? { state: "available", message: `@${data.username} is available` }
              : { state: "taken", message: data.reason || "That username is taken" }
          )
        )
        .catch(() => setResult({ state: "error", message: "" }));
    }, 350);
    return () => clearTimeout(timer);
  }, [username]);

  return result;
}

export default function Signup() {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const availability = useUsernameAvailability(username);

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await signup({ username, name: name.trim(), email: email.trim() || null });
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.message);
      setSubmitting(false);
    }
  }

  const blocked = availability.state === "invalid" || availability.state === "taken";

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#0B3D2E] text-[#F8F6E9] relative overflow-hidden px-4">
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
        <p className="text-center text-sm opacity-80 mb-6">Pick a unique username -- it's what you'll log in with</p>

        <div>
          <label htmlFor="username" className="block text-sm font-medium mb-1">
            Username
          </label>
          <div className="relative">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 opacity-50">@</span>
            <input
              id="username"
              type="text"
              required
              autoComplete="username"
              autoCapitalize="none"
              spellCheck={false}
              maxLength={24}
              value={username}
              onChange={(event) => setUsername(event.target.value.toLowerCase().replace(/\s/g, ""))}
              aria-describedby="username-status"
              aria-invalid={blocked}
              className={`${inputClass} pl-8 pr-10`}
            />
            <span className="absolute right-3 top-1/2 -translate-y-1/2">
              {availability.state === "checking" && <Loader2 size={18} className="animate-spin opacity-60" />}
              {availability.state === "available" && <CheckCircle2 size={18} className="text-[#81C784]" />}
              {blocked && <XCircle size={18} className="text-red-400" />}
            </span>
          </div>
          <p
            id="username-status"
            aria-live="polite"
            className={`mt-1 text-xs ${blocked ? "text-red-300" : availability.state === "available" ? "text-[#81C784]" : "opacity-60"}`}
          >
            {availability.message || USERNAME_HINT}
          </p>
        </div>

        <div>
          <label htmlFor="name" className="block text-sm font-medium mb-1">
            Display name
          </label>
          <input
            id="name"
            type="text"
            required
            autoComplete="name"
            maxLength={100}
            value={name}
            onChange={(event) => setName(event.target.value)}
            className={inputClass}
          />
        </div>

        <div>
          <label htmlFor="email" className="block text-sm font-medium mb-1">
            Email <span className="opacity-60 font-normal">(optional)</span>
          </label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className={inputClass}
          />
        </div>

        {error && (
          <p role="alert" className="text-sm text-red-400 bg-red-400/10 p-3 rounded-lg text-center border border-red-400/20">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={submitting || blocked}
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
