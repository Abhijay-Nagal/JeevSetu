// The login token lives in localStorage so a refresh keeps you signed in.
// Every read/write is guarded: storage can be unavailable (private mode,
// blocked site data) and the app should still work for that tab.
const TOKEN_KEY = "jeevsetu.token";

export const SESSION_EXPIRED_EVENT = "jeevsetu:session-expired";

export function getToken() {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setToken(token) {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  } catch {
    // Storage unavailable -- the session just won't survive a refresh.
  }
}
