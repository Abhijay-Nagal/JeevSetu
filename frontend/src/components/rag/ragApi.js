const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const USE_MOCK =
  import.meta.env.VITE_RAG_USE_MOCK === "true";

/**
 * Development-only mock response.
 * This allows the frontend to be developed before
 * the FastAPI RAG backend is fully available.
 */
async function mockQueryBNHS(question) {
  await new Promise((resolve) =>
    setTimeout(resolve, 1200),
  );

  return {
    answer:
      `This is a frontend development response for:\n\n"${question}"\n\n` +
      "The production version will retrieve relevant BNHS documents, " +
      "send the grounded context to the LLM, and return an answer with citations.",
    sources: [
      {
        title: "JBNHS — Development Source",
        excerpt:
          "Development placeholder used to validate the RAG frontend source-display experience.",
      },
      {
        title: "Hornbill — Development Source",
        excerpt:
          "Development placeholder used to validate the BNHS evidence panel.",
      },
    ],
  };
}

/**
 * Production RAG request.
 *
 * Backend contract:
 *
 * POST /rag/query
 *
 * Request:
 * {
 *   question: string
 * }
 *
 * Response:
 * {
 *   answer: string,
 *   sources: [
 *     {
 *       title: string,
 *       excerpt: string
 *     }
 *   ]
 * }
 */
async function productionQueryBNHS(
  question,
  accessToken = null,
) {
  const cleanedQuestion = question.trim();

  if (!cleanedQuestion) {
    throw new Error("Please enter a question.");
  }

  const headers = {
    "Content-Type": "application/json",
  };

  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`;
  }

  let response;

  try {
    response = await fetch(
      `${API_BASE_URL}/rag/query`,
      {
        method: "POST",
        headers,
        body: JSON.stringify({
          question: cleanedQuestion,
        }),
      },
    );
  } catch {
    throw new Error(
      "Cannot connect to the BNHS backend. Please make sure FastAPI is running on the configured API URL.",
    );
  }

  let data = null;

  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    let message =
      `Request failed with status ${response.status}.`;

    if (
      data &&
      typeof data === "object" &&
      typeof data.detail === "string"
    ) {
      message = data.detail;
    }

    throw new Error(message);
  }

  if (
    !data ||
    typeof data !== "object" ||
    typeof data.answer !== "string"
  ) {
    throw new Error(
      "The BNHS RAG backend returned an invalid response.",
    );
  }

  const sources = Array.isArray(data.sources)
    ? data.sources
        .filter(
          (source) =>
            source &&
            typeof source === "object",
        )
        .map((source) => ({
          title:
            typeof source.title === "string"
              ? source.title
              : "BNHS Source",
          excerpt:
            typeof source.excerpt === "string"
              ? source.excerpt
              : "",
        }))
    : [];

  return {
    answer: data.answer,
    sources,
  };
}

export async function queryBNHS(
  question,
  accessToken = null,
) {
  if (USE_MOCK) {
    return mockQueryBNHS(question);
  }

  return productionQueryBNHS(
    question,
    accessToken,
  );
}