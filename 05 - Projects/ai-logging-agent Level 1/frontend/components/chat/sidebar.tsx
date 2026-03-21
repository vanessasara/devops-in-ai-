import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { ThemeToggle } from "@/components/theme-toggle"
import { type Message } from "@/lib/api"
import { MessageSquare, Trash2, Terminal } from "lucide-react"

const EXAMPLE_QUESTIONS = [
  "What log files are available?",
  "Read sample_app.log",
  "Search for ERROR in sample_app.log",
  "Summarise everything and save it",
]

interface SidebarProps {
  messages: Message[]
  loading: boolean
  onExampleClick: (q: string) => void
  onClear: () => void
}

function PreviousMessages({ messages }: { messages: Message[] }) {
  const userMessages = messages.filter((m) => m.role === "user")

  if (userMessages.length === 0) return null

  return (
    <div>
      <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
        This session
      </p>
      <div className="flex flex-col gap-1">
        {userMessages.map((m) => (
          <div
            key={m.id}
            className="flex items-start gap-2 px-2.5 py-1.5 rounded-lg text-xs text-muted-foreground"
          >
            <MessageSquare className="h-3 w-3 mt-0.5 shrink-0 text-violet-400" />
            <span className="truncate">{m.content}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export function Sidebar({ messages, loading, onExampleClick, onClear }: SidebarProps) {
  return (
    <div className="w-64 shrink-0 flex flex-col h-full border-r bg-muted/30">

      {/* Header */}
      <div className="p-4 border-b flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="h-7 w-7 rounded-lg bg-gradient-to-br from-violet-500 to-emerald-500 flex items-center justify-center">
            <Terminal className="h-3.5 w-3.5 text-white" />
          </div>
          <div>
            <p className="text-sm font-semibold leading-none">Log Analyzer</p>
            <p className="text-[10px] text-muted-foreground mt-0.5">Gemini · Agents SDK</p>
          </div>
        </div>
        <ThemeToggle />
      </div>

      <ScrollArea className="flex-1 p-4">
        <div className="flex flex-col gap-5">

          {/* Example questions */}
          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
              Try asking
            </p>
            <div className="flex flex-col gap-1">
              {EXAMPLE_QUESTIONS.map((q) => (
                <button
                  key={q}
                  onClick={() => onExampleClick(q)}
                  disabled={loading}
                  className="text-left text-xs text-foreground/70 hover:text-foreground hover:bg-violet-50 dark:hover:bg-violet-950/30 rounded-lg px-2.5 py-1.5 transition-colors disabled:opacity-50 disabled:cursor-not-allowed border border-transparent hover:border-violet-100 dark:hover:border-violet-900"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          {/* Previous messages in this session */}
          <PreviousMessages messages={messages} />

        </div>
      </ScrollArea>

      {/* Footer */}
      <div className="p-4 border-t">
        <Button
          variant="ghost"
          size="sm"
          onClick={onClear}
          disabled={loading || messages.length === 0}
          className="w-full text-xs text-muted-foreground hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30 gap-2"
        >
          <Trash2 className="h-3.5 w-3.5" />
          Clear chat
        </Button>
      </div>

    </div>
  )
}