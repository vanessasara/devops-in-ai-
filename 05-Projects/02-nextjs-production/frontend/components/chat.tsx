"use client"

import { useState } from "react"
import { Sidebar } from "@/components/chat/sidebar"
import { ChatMessages } from "@/components/chat/chat-message"
import { ChatInput } from "@/components/chat/chat-input"
import { sendMessage, type Message } from "@/lib/api"
import { useSessions } from "@/lib/hooks/use-sessions"

export function Chat() {
  const { sessions, activeSession, updateMessages, newSession, switchSession, deleteSession } =
    useSessions()
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const messages = activeSession?.messages ?? []

  async function handleSubmit(message: string) {
    if (!message.trim() || loading) return

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: message.trim(),
      timestamp: Date.now(),
    }

    const updated = [...messages, userMessage]
    updateMessages(updated)
    setInput("")
    setError(null)
    setLoading(true)

    try {
      const response = await sendMessage(message.trim())
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response,
        timestamp: Date.now(),
      }
      updateMessages([...updated, assistantMessage])
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-screen bg-background">
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSession?.id ?? ""}
        loading={loading}
        onExampleClick={handleSubmit}
        onNewSession={newSession}
        onSwitchSession={switchSession}
        onDeleteSession={deleteSession}
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
