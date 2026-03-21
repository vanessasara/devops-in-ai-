import { useRef, useEffect } from "react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { MessageBubble } from "./message-bubble"
import { TypingIndicator } from "./typing-indicator"
import { type Message } from "@/lib/api"
import { Terminal } from "lucide-react"

interface ChatMessagesProps {
  messages: Message[]
  loading: boolean
  error: string | null
}

export function ChatMessages({ messages, loading, error }: ChatMessagesProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, loading])

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-3 text-center p-8">
        <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-violet-500 to-emerald-500 flex items-center justify-center shadow-lg">
          <Terminal className="h-6 w-6 text-white" />
        </div>
        <p className="text-sm font-medium text-foreground">Ask me about your logs</p>
        <p className="text-xs text-muted-foreground max-w-48">
          I can read, search, and analyse your log files in plain language
        </p>
      </div>
    )
  }

  return (
    <ScrollArea className="flex-1 px-4 pt-4">
      <div className="flex flex-col gap-4 pb-4">
        {messages.map((m) => (
          <MessageBubble key={m.id} message={m} />
        ))}
        {loading && <TypingIndicator />}
        {error && (
          <div className="text-xs text-red-500 bg-red-50 dark:bg-red-950/30 border border-red-100 dark:border-red-900 rounded-xl px-3 py-2">
            {error}
          </div>
        )}
        <div ref={bottomRef} />
      </div>
    </ScrollArea>
  )
}