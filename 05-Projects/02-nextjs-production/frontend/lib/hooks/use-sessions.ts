"use client"

import { useCallback, useEffect } from "react"
import { useLocalStorage } from "./use-local-storage"
import { type Message } from "@/lib/api"

export interface Session {
  id: string
  title: string
  createdAt: number
  messages: Message[]
}

const MAX_SESSIONS = 20

function createSession(): Session {
  return {
    id: crypto.randomUUID(),
    title: "New chat",
    createdAt: Date.now(),
    messages: [],
  }
}

export function useSessions() {
  const [sessions, setSessions] = useLocalStorage<Session[]>("chat_sessions", [createSession()])
  const [activeId, setActiveId] = useLocalStorage<string>("chat_active_session", "")

  useEffect(() => {
    if (sessions.length === 0) return
    if (!activeId || !sessions.some((s) => s.id === activeId)) {
      setActiveId(sessions[0].id)
    }
  }, [sessions, activeId, setActiveId])

  const activeSession = sessions.find((s) => s.id === activeId) ?? sessions[0]

  const updateMessages = useCallback(
    (messages: Message[]) => {
      setSessions((prev) =>
        prev.map((s) => {
          if (s.id !== activeId) return s
          const title =
            messages.find((m) => m.role === "user")?.content.slice(0, 40) ?? "New chat"
          return { ...s, messages, title }
        })
      )
    },
    [activeId, setSessions]
  )

  const newSession = useCallback(() => {
    const session = createSession()
    setSessions((prev) => {
      const updated = [session, ...prev]
      return updated.slice(0, MAX_SESSIONS)
    })
    setActiveId(session.id)
  }, [setSessions, setActiveId])

  const switchSession = useCallback(
    (id: string) => {
      setActiveId(id)
    },
    [setActiveId]
  )

  const deleteSession = useCallback(
    (id: string) => {
      setSessions((prev) => {
        const updated = prev.filter((s) => s.id !== id)
        if (updated.length === 0) {
          const fresh = createSession()
          setActiveId(fresh.id)
          return [fresh]
        }
        if (id === activeId) setActiveId(updated[0].id)
        return updated
      })
    },
    [activeId, setSessions, setActiveId]
  )

  return {
    sessions,
    activeSession,
    updateMessages,
    newSession,
    switchSession,
    deleteSession,
  }
}
