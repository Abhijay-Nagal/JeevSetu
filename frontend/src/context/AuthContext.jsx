import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api } from "../lib/api";
import { getToken, setToken, SESSION_EXPIRED_EVENT } from "../lib/session";

const AuthContext = createContext(undefined);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  // Only "loading" while there's a stored token to check -- with no token
  // there's nothing to wait for.
  const [loading, setLoading] = useState(() => Boolean(getToken()));

  useEffect(() => {
    if (!getToken()) return;
    let cancelled = false;
    api
      .me()
      .then((profile) => !cancelled && setUser(profile))
      .catch(() => !cancelled && setUser(null))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const handleExpired = () => setUser(null);
    window.addEventListener(SESSION_EXPIRED_EVENT, handleExpired);
    return () => window.removeEventListener(SESSION_EXPIRED_EVENT, handleExpired);
  }, []);

  const startSession = useCallback(({ access_token, user: profile }) => {
    setToken(access_token);
    setUser(profile);
    return profile;
  }, []);

  const login = useCallback(
    async (username) => startSession(await api.login(username)),
    [startSession]
  );

  const signup = useCallback(async (details) => startSession(await api.signup(details)), [startSession]);

  const signOut = useCallback(() => {
    setToken(null);
    setUser(null);
  }, []);

  const value = { user, loading, login, signup, signOut };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
