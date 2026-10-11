import { api } from "../../lib/api";

// Sends the question with the recent conversation so follow-ups ("what does
// it eat?") are answered in context.
export function queryBNHS(question, history = []) {
  return api.askBNHS(
    question,
    history.slice(-6).map(({ role, content }) => ({ role, content: content.slice(0, 4000) }))
  );
}
