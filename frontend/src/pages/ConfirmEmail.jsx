import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { CheckCircle2, XCircle, Loader2 } from "lucide-react";
import { api } from "../lib/api";

export const route = { path: "/confirm-email" };

export default function ConfirmEmail() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const [status, setStatus] = useState("loading"); // loading | success | error
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setError("Missing confirmation token.");
      return;
    }

    api
      .confirmEmail(token)
      .then(() => setStatus("success"))
      .catch((err) => {
        setStatus("error");
        setError(err.message);
      });
  }, [token]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#F8F6E9] text-[#0B3D2E] px-4">
      <div className="w-full max-w-sm rounded-2xl border border-[#0B3D2E]/10 bg-white p-8 text-center">
        {status === "loading" && (
          <>
            <Loader2 size={32} className="mx-auto animate-spin text-[#0B3D2E]/40" />
            <p className="mt-4 text-sm text-[#0B3D2E]/70">Confirming your email...</p>
          </>
        )}

        {status === "success" && (
          <>
            <CheckCircle2 size={40} className="mx-auto text-[#2E7D32]" />
            <h1 className="mt-4 text-xl font-bold">Email confirmed</h1>
            <p className="mt-2 text-sm text-[#0B3D2E]/70">
              Your account is ready. You can now log in to JeevSetu.
            </p>
            <Link
              to="/login"
              className="mt-6 inline-block rounded-lg bg-[#0B3D2E] px-6 py-2.5 text-sm font-medium text-white"
            >
              Go to login
            </Link>
          </>
        )}

        {status === "error" && (
          <>
            <XCircle size={40} className="mx-auto text-red-500" />
            <h1 className="mt-4 text-xl font-bold">Confirmation failed</h1>
            <p className="mt-2 text-sm text-[#0B3D2E]/70">{error}</p>
            <Link to="/signup" className="mt-6 inline-block text-sm underline">
              Back to signup
            </Link>
          </>
        )}
      </div>
    </div>
  );
}
