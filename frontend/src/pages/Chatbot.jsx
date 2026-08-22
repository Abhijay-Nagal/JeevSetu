export const route = { path: "/chatbot", layout: "app" }

function Chatbot() {
  return (
    <div>
      <h1 className="text-3xl font-semibold">Chatbot</h1>
      <p className="mt-2 opacity-70">
        Your wildlife conservation assistant.
      </p>
    </div>
  )
}

export default Chatbot