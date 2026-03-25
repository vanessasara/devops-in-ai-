import { useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { SendHorizonal } from "lucide-react"

interface ChatInputProps {
  value: string
  onChange: (v: string) => void
  onSubmit: (v: string) => void
  disabled: boolean
}

export function ChatInput({ value, onChange, onSubmit, disabled }: ChatInputProps) {
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (!disabled) inputRef.current?.focus()
  }, [disabled])

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      onSubmit(value)
    }
  }

  return (
    <div className="p-4 border-t bg-background">
      <div className="flex gap-2 items-center">
        <Input
          ref={inputRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about your logs..."
          disabled={disabled}
          className="flex-1 text-sm rounded-xl bg-muted border-0 focus-visible:ring-1 focus-visible:ring-violet-400"
          autoFocus
        />
        <Button
          onClick={() => onSubmit(value)}
          disabled={disabled || !value.trim()}
          size="icon"
          className="rounded-xl bg-violet-600 hover:bg-violet-700 text-white shrink-0"
        >
          <SendHorizonal className="h-4 w-4" />
        </Button>
      </div>
      <p className="text-[10px] text-muted-foreground mt-1.5 px-1">
        Press Enter to send
      </p>
    </div>
  )
}