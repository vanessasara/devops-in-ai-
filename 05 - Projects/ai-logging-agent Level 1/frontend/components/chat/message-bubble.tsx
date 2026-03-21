import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { type Message } from "@/lib/api"
import { Bot, User } from "lucide-react"

export function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user"

  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"}`}>
      <Avatar className="h-8 w-8 shrink-0 ring-2 ring-offset-1 ring-offset-background">
        <AvatarFallback
          className={
            isUser
              ? "bg-violet-600 text-white ring-violet-400"
              : "bg-emerald-500 text-white ring-emerald-400"
          }
        >
          {isUser
            ? <User className="h-4 w-4" />
            : <Bot className="h-4 w-4" />
          }
        </AvatarFallback>
      </Avatar>

      <div
        className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap break-words shadow-sm ${
          isUser
            ? "bg-violet-600 text-white rounded-tr-sm"
            : "bg-muted text-foreground rounded-tl-sm"
        }`}
      >
        {message.content}
      </div>
    </div>
  )
}