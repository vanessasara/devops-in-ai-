"use client"

import { useState } from "react"
import { Sidebar } from "@/components/chat/sidebar"
import { ChatMessages } from "@/components/chat/chat-message"
import { ChatInput } from "@/components/chat/chat-input"
import { sendMessage, type Message } from "@/lib/api"

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(message: string) {
    if (!message.trim() || loading) return

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: message.trim(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setError(null)
    setLoading(true)

    try {
      const response = await sendMessage(message.trim())
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: "assistant", content: response },
      ])
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong")
    } finally {
      setLoading(false)
    }
  }

  function clearChat() {
    setMessages([])
    setError(null)
  }

  return (
    <div className="flex h-screen bg-background">
      <Sidebar
        messages={messages}
        loading={loading}
        onExampleClick={handleSubmit}
        onClear={clearChat}
      />
      <div className="flex-1 flex flex-col overflow-hidden">
        <ChatMessages messages={messages} loading={loading} error={error} />
        <ChatInput
          value={input}
          onChange={setInput}
          onSubmit={handleSubmit}
          disabled={loading}
        />
      </div>
    </div>
  )
}