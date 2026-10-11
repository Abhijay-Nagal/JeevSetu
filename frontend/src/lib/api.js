import { getToken, setToken, SESSION_EXPIRED_EVENT } from "./session";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

async function request(path, options = {}) {
  const token = getToken();
  const isFormData = options.body instanceof FormData;

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        ...(isFormData ? {} : { "Content-Type": "application/json" }),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
    });
  } catch {
    throw new Error("Can't reach the JeevSetu server. Check that the backend is running.");
  }

  if (response.status === 401 && token) {
    // Token expired or was revoked: drop it so the app shows the login
    // prompt instead of failing every request.
    setToken(null);
    window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT));
  }

  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("text/html")) {
    throw new Error("Backend API is unreachable. Please configure VITE_API_BASE_URL for production.");
  }

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(errorMessage(body.detail) || `Request failed: ${response.status}`);
  }

  if (response.status === 204) return null;
  return response.json();
}

// FastAPI validation errors arrive as a list of {loc, msg}; turn them into
// one readable sentence instead of "[object Object]".
function errorMessage(detail) {
  if (!detail) return null;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => (item.msg || "").replace(/^Value error, /, ""))
      .filter(Boolean)
      .join(". ");
  }
  return null;
}

export const api = {
  listCommunities: () => request("/communities"),
  myCommunities: () => request("/communities/mine"),
  createCommunity: (body) => request("/communities", { method: "POST", body: JSON.stringify(body) }),
  joinCommunity: (slug) => request(`/communities/${slug}/join`, { method: "POST" }),
  leaveCommunity: (slug) => request(`/communities/${slug}/leave`, { method: "DELETE" }),
  getCommunityFeed: (slug) => request(`/communities/${slug}/feed`),
  listAllPosts: () => request("/observations"),
  createPost: (body) => request("/observations", { method: "POST", body: JSON.stringify(body) }),
  myPosts: () => request("/observations/mine"),
  likePost: (id) => request(`/observations/${id}/like`, { method: "POST" }),
  unlikePost: (id) => request(`/observations/${id}/like`, { method: "DELETE" }),
  listComments: (id) => request(`/observations/${id}/comments`),
  addComment: (id, content) =>
    request(`/observations/${id}/comments`, { method: "POST", body: JSON.stringify({ content }) }),
  searchKnowledgeHub: (query, limit = 10) =>
    request("/search", { method: "POST", body: JSON.stringify({ query, limit }) }),
  getNextSteps: (currentResource, userInterests = []) =>
    request("/next-steps", {
      method: "POST",
      body: JSON.stringify({ current_resource: currentResource, user_interests: userInterests }),
    }),
  getQuiz: (topic, numQuestions = 5) =>
    request("/quiz", { method: "POST", body: JSON.stringify({ topic, num_questions: numQuestions }) }),
  getWallet: () => request("/rewards/wallet"),
  signup: (body) => request("/auth/signup", { method: "POST", body: JSON.stringify(body) }),
  login: (username, password) =>
    request("/auth/login", { method: "POST", body: JSON.stringify({ username, password }) }),
  me: () => request("/auth/me"),
  checkUsername: (username) => request(`/auth/username-available?username=${encodeURIComponent(username)}`),
  sendConfirmationEmail: () => request("/auth/send-confirmation", { method: "POST" }),
  confirmEmail: (token) =>
    request("/auth/confirm-email", { method: "POST", body: JSON.stringify({ token }) }),
  getDailyQuestion: () => request("/rewards/daily-question"),
  answerDailyQuestion: (selectedAnswer) =>
    request("/rewards/daily-question/answer", {
      method: "POST",
      body: JSON.stringify({ selected_answer: selectedAnswer }),
    }),
  checkRelatedRecords: (abstract) =>
    request("/research/check-related", { method: "POST", body: JSON.stringify({ abstract }) }),
  submitResearch: (body) =>
    request("/research/submissions", { method: "POST", body: JSON.stringify(body) }),
  myResearchSubmissions: () => request("/research/submissions/mine"),
  askBNHS: (question, history = []) =>
    request("/ask", { method: "POST", body: JSON.stringify({ question, history }) }),
  uploadImage: (file) => {
    const form = new FormData();
    form.append("file", file);
    return request("/uploads", { method: "POST", body: form });
  },
  getNotifications: () => request("/notifications"),
  getCards: () => request("/cards"),
  collectCard: (cardId) => request(`/cards/${encodeURIComponent(cardId)}/collect`, { method: "POST" }),
};
