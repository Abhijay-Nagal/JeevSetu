import { supabase } from "./supabaseClient";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

async function request(path, options = {}) {
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${response.status}`);
  }

  if (response.status === 204) return null;

  const contentType = response.headers.get("content-type");
  if (contentType && contentType.includes("text/html")) {
    throw new Error("Backend API is unreachable. Please configure VITE_API_BASE_URL for production.");
  }

  return response.json();
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
  sendConfirmationEmail: (userId, email, name) =>
    request("/auth/send-confirmation", {
      method: "POST",
      body: JSON.stringify({ user_id: userId, email, name }),
    }),
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
};
