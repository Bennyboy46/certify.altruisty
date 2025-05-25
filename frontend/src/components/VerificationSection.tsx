"use client";

import { useState, FormEvent, useRef, useEffect } from "react";

interface Message {
  text: string;
  sender: "user" | "bot";
}

export default function VerificationSection() {
  const [messages, setMessages] = useState<Message[]>([
    {
      text: "Hello! I am your certificate verification bot. Please enter the Certificate ID to verify.",
      sender: "bot",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e: FormEvent) => {
    e.preventDefault();
    if (input.trim() === "") return;

    const userMessage: Message = { text: input, sender: "user" };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch(
        "http://localhost:8000/verify-certificate-chatbot",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            text: userMessage.text,
            conversation_id: conversationId,
          }),
        }
      );

      const data = await response.json();

      setConversationId(data.conversation_id);

      let botMessageText = data.response;

      if (data.certificate_found && data.owner_info) {
        const ownerInfo = data.owner_info;
        botMessageText += `\nOwner: ${ownerInfo.recipient_name}\nCourse: ${ownerInfo.course_name}\nIssued On: ${ownerInfo.issue_date}\nCertificate ID: ${ownerInfo.certificate_id}`;
      }

      const botMessage: Message = { text: botMessageText, sender: "bot" };
      setMessages((prevMessages) => [...prevMessages, botMessage]);
    } catch (error) {
      console.error("Error verifying certificate:", error);
      const errorMessage: Message = {
        text: "Sorry, I could not connect to the verification service.",
        sender: "bot",
      };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg shadow-md p-6 border border-gray-700 flex flex-col h-96">
      <h2 className="text-xl font-semibold mb-4 text-white">
        Certificate Verification Chatbot
      </h2>
      <div
        className="flex-1 overflow-y-auto mb-4 pr-2"
        style={{ scrollbarWidth: "thin", scrollbarColor: "#4A5568 #2D3748" }}
      >
        {messages.map((message, index) => (
          <div
            key={index}
            className={`mb-3 ${
              message.sender === "user" ? "text-right" : "text-left"
            }`}
          >
            <span
              className={`inline-block px-4 py-2 rounded-lg ${
                message.sender === "user"
                  ? "bg-indigo-600 text-white"
                  : "bg-gray-700 text-gray-200"
              }`}
              style={{ maxWidth: "70%", overflowWrap: "break-word" }}
            >
              {message.text.split("\n").map((line, i) => (
                <p key={i}>{line}</p>
              ))}
            </span>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={handleSend} className="flex">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter Certificate ID..."
          className="flex-1 rounded-l-md bg-gray-700 border-gray-600 text-white placeholder-gray-400 focus:border-indigo-500 focus:ring-indigo-500"
          disabled={loading}
        />
        <button
          type="submit"
          className="px-4 py-2 bg-indigo-600 text-white rounded-r-md hover:bg-indigo-700 transition-colors disabled:opacity-50"
          disabled={loading}
        >
          Send
        </button>
      </form>
    </div>
  );
}
