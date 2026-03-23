"use client"

import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { ThemeToggle } from "@/components/theme-toggle"
import { type Session } from "@/lib/hooks/use-sessions"
import { MessageSquare, Trash2, Terminal, Plus } from "lucide-react"
import { formatDistanceToNow } from "date-fns"

const EXAMPLE_QUESTIONS = [
  "What log files are available?",
  "Read sample_app.log",
  "Search for ERROR in sample_app.log",
  "Summarise everything and save it",
]

interface SidebarProps {
  sessions: Session[]
  activeSessionId: string
  loading: boolean
  onExampleClick: (q: string) => void
  onNewSession: () => void
  onSwitchSession: (id: string) => void
  onDeleteSession: (id: string) => void
}

export function Sidebar({
  sessions,
  activeSessionId,
  loading,
  onExampleClick,
  onNewSession,
  onSwitchSession,
  onDeleteSession,
}: SidebarProps) {
  return (
    <div className="w-64 shrink-0 flex flex-col h-full border-r bg-muted/30">
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

      <div className="p-3 border-b">
        <Button
          onClick={onNewSession}
          variant="outline"
          size="sm"
          className="w-full gap-2 text-xs"
        >
          <Plus className="h-3.5 w-3.5" /> New chat
        </Button>
      </div>

      <ScrollArea className="flex-1 p-3">
        <div className="flex flex-col gap-4">
          {sessions.length > 0 && (
            <div>
              <p className="text-[10px] font-medium text-muted-foreground uppercase tracking-wide mb-2 px-1">
                Recent chats
              </p>
              <div className="flex flex-col gap-1">
                {sessions.map((s) => (
                  <div
                    key={s.id}
                    className={`group flex items-center gap-2 px-2.5 py-2 rounded-lg cursor-pointer transition-colors ${
                      s.id === activeSessionId
                        ? "bg-violet-50 dark:bg-violet-950/30 border border-violet-100 dark:border-violet-900"
                        : "hover:bg-muted"
                    }`}
                    onClick={() => onSwitchSession(s.id)}
                  >
                    <MessageSquare className="h-3 w-3 shrink-0 text-violet-400" />
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-foreground truncate">{s.title}</p>
                      <p className="text-[10px] text-muted-foreground">
                        {formatDistanceToNow(s.createdAt, { addSuffix: true })}
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation()
                        onDeleteSession(s.id)
                      }}
                      className="opacity-0 group-hover:opacity-100 text-muted-foreground hover:text-red-500 transition-all"
                    >
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div>
            <p className="text-[10px] font-medium text-muted-foreground uppercase tracking-wide mb-2 px-1">
              Try asking
            </p>
            <div className="flex flex-col gap-1">
              {EXAMPLE_QUESTIONS.map((q) => (
                <button
                  key={q}
                  type="button"
                  onClick={() => onExampleClick(q)}
                  disabled={loading}
                  className="text-left text-xs text-foreground/70 hover:text-foreground hover:bg-violet-50 dark:hover:bg-violet-950/30 rounded-lg px-2.5 py-1.5 transition-colors disabled:opacity-50"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        </div>
      </ScrollArea>
    </div>
  )
}
