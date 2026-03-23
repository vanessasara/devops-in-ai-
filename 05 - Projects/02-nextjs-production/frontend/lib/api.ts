const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  /** Present on new messages; older localStorage data may omit */
  timestamp?: number
}

export async function sendMessage(message: string): Promise<string> {
  const res = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  })

  if (!res.ok) {
    const error = await res.json().catch(() => ({}))
    throw new Error(error.detail ?? `Request failed: ${res.status}`)
  }

  const data = await res.json()
  return data.response
}