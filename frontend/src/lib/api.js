import { supabase } from "./supabaseClient";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

if (!API_BASE_URL) {
  throw new Error("Missing VITE_API_BASE_URL -- copy .env.example to .env and fill it in.");
}

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
  searchKnowledgeHub: (query, limit = 10) =>
    request("/api/search", { method: "POST", body: JSON.stringify({ query, limit }) }),
  getNextSteps: (currentResource, userInterests = []) =>
    request("/api/next-steps", {
      method: "POST",
      body: JSON.stringify({ current_resource: currentResource, user_interests: userInterests }),
    }),
  getQuiz: (topic, numQuestions = 5) =>
    request("/api/quiz", { method: "POST", body: JSON.stringify({ topic, num_questions: numQuestions }) }),
  getWallet: () => request("/rewards/wallet"),
};
