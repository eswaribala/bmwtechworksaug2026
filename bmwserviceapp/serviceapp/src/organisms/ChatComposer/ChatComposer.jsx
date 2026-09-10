import { useRef, useState } from "react";
import PromptInput from "../../atoms/PromptInput/PromptInput";
import ComposerToolbar from "../../molecules/ToolComposer/ToolComposer";
import QuickLinks from "../../molecules/QuickLinks/QuickLinks";


const RAG_API_URL = import.meta.env.VITE_RAG_API_URL;

export default function ChatComposer() {
  const [message, setMessage] = useState("");

  // Values must match Models.js and Clients.js values.
  const [model, setModel] = useState("gpt-5.6-terra-light");
  const [client, setClient] = useState("bmw");

  const [chatMessages, setChatMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const inputRef = useRef(null);

  async function sendMessage() {
    const cleanMessage = message.trim();

    if (!cleanMessage || isLoading) {
      return;
    }

    // Show the question in UI immediately.
    setChatMessages((currentMessages) => [
      ...currentMessages,
      {
        role: "user",
        content: cleanMessage,
      },
    ]);

    setMessage("");
    setIsLoading(true);

    try {
      const response = await fetch(
        `${RAG_API_URL}/ask?client=${client}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: cleanMessage,
          }),
        },
      );

      if (!response.ok) {
        throw new Error(`RAG API failed with status ${response.status}`);
      }

      const data = await response.json();

      // Expected API response: { "answer": "..." }
      const ragAnswer =
        data.answer ||
        data.response ||
        data.message ||
        "The RAG service did not return an answer.";

      // Show RAG answer in UI.
      setChatMessages((currentMessages) => [
        ...currentMessages,
        {
          role: "assistant",
          content: ragAnswer,
        },
      ]);
    } catch (error) {
      console.error("RAG API error:", error);

      setChatMessages((currentMessages) => [
        ...currentMessages,
        {
          role: "assistant",
          content:
            "Unable to connect to the RAG API. Ensure FastAPI is running at http://127.0.0.1:8000.",
          isError: true,
        },
      ]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  }

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }

  return (
    <main className="min-h-screen bg-white px-4 pt-8 sm:px-7">
      <h1 className="mb-8 text-center text-3xl font-normal tracking-tight text-neutral-950 sm:text-4xl">
        What should we work on?
      </h1>

      {/* RAG question and answer area */}
      <section className="mx-auto mb-6 w-full max-w-6xl space-y-4">
        {chatMessages.map((chat, index) => (
          <div
            key={`${chat.role}-${index}`}
            className={`max-w-3xl whitespace-pre-wrap rounded-2xl px-5 py-4 text-base leading-7 shadow-sm ${
              chat.role === "user"
                ? "ml-auto bg-blue-600 text-white"
                : chat.isError
                  ? "mr-auto bg-red-50 text-red-700"
                  : "mr-auto bg-neutral-100 text-neutral-900"
            }`}
          >
            {chat.content}
          </div>
        ))}

        {isLoading && (
          <div className="mr-auto w-fit rounded-2xl bg-neutral-100 px-5 py-4 text-neutral-500">
            Searching {client.toUpperCase()} documents...
          </div>
        )}
      </section>

      {/* Input composer */}
      <section className="mx-auto h-48 w-full max-w-6xl overflow-hidden rounded-[40px] border border-neutral-200 bg-white shadow-[0_18px_36px_rgba(0,0,0,0.06)]">
        <PromptInput
          ref={inputRef}
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          onKeyDown={handleKeyDown}
        />

        <ComposerToolbar
          message={message}
          model={model}
          client={client}
          onClientChange={(event) => setClient(event.target.value)}
          onModelChange={(event) => setModel(event.target.value)}
          onSend={sendMessage}
        />
      </section>

      <QuickLinks />
    </main>
  );
}