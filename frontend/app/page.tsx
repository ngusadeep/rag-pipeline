"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Spinner } from "@/components/ui/spinner"
import { ThemeToggle } from "@/components/theme-toggle"
import { sendChatMessage, type ChatResponse, type SourceChunk } from "@/lib/api"
import Link from "next/link"
import { Send, Bot, User, FileText } from "lucide-react"

interface Message {
  role: "user" | "assistant"
  content: string
  sources?: SourceChunk[]
}

export default function Home() {
  const [question, setQuestion] = useState("")
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!question.trim() || loading) return

    const userMessage: Message = {
      role: "user",
      content: question,
    }
    setMessages((prev) => [...prev, userMessage])
    setQuestion("")
    setLoading(true)

    try {
      const response: ChatResponse = await sendChatMessage({
        question: userMessage.content,
        top_k: 4,
      })

      const assistantMessage: Message = {
        role: "assistant",
        content: response.answer,
        sources: response.sources,
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage: Message = {
        role: "assistant",
        content: error instanceof Error ? error.message : "Failed to get response",
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-svh flex-col">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary text-primary-foreground">
              <Bot className="h-4 w-4" />
            </div>
            <div>
              <h1 className="text-lg font-semibold">RAG Chat</h1>
              <p className="text-xs text-muted-foreground">
                Ask questions about your documents
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <Link href="/login">
              <Button variant="outline" size="sm">
                Admin Login
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Chat Messages Area */}
      <div className="flex-1 overflow-hidden">
        <div className="h-full overflow-y-auto">
          <div className="container mx-auto max-w-3xl px-4 py-6">
            {messages.length === 0 ? (
              <div className="flex h-full items-center justify-center">
                <div className="text-center space-y-4 max-w-md">
                  <div className="flex justify-center">
                    <div className="flex h-16 w-16 items-center justify-center rounded-full bg-muted">
                      <Bot className="h-8 w-8 text-muted-foreground" />
                    </div>
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold mb-2">
                      Start a conversation
                    </h2>
                    <p className="text-sm text-muted-foreground">
                      Ask questions about your documents and get intelligent answers powered by RAG.
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex gap-4 ${
                      message.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    {message.role === "assistant" && (
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
                        <Bot className="h-4 w-4" />
                      </div>
                    )}
                    <div
                      className={`flex flex-col gap-2 max-w-[80%] ${
                        message.role === "user" ? "items-end" : "items-start"
                      }`}
                    >
                      <div
                        className={`rounded-2xl px-4 py-3 ${
                          message.role === "user"
                            ? "bg-primary text-primary-foreground rounded-br-sm"
                            : "bg-muted rounded-bl-sm"
                        }`}
                      >
                        <p className="text-sm leading-relaxed whitespace-pre-wrap">
                          {message.content}
                        </p>
                      </div>
                      {message.sources && message.sources.length > 0 && (
                        <div className="space-y-2 w-full">
                          <p className="text-xs font-medium text-muted-foreground px-1">
                            Sources ({message.sources.length})
                          </p>
                          <div className="space-y-1.5">
                            {message.sources.map((source, idx) => (
                              <div
                                key={idx}
                                className="flex items-start gap-2 rounded-lg border bg-card p-2.5 text-xs"
                              >
                                <FileText className="h-3.5 w-3.5 shrink-0 mt-0.5 text-muted-foreground" />
                                <p className="line-clamp-2 text-muted-foreground">
                                  {source.content}
                                </p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                    {message.role === "user" && (
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted">
                        <User className="h-4 w-4" />
                      </div>
                    )}
                  </div>
                ))}
                {loading && (
                  <div className="flex gap-4 justify-start">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
                      <Bot className="h-4 w-4" />
                    </div>
                    <div className="flex flex-col gap-2">
                      <div className="rounded-2xl rounded-bl-sm bg-muted px-4 py-3">
                        <div className="flex items-center gap-2">
                          <Spinner className="h-4 w-4" />
                          <span className="text-sm text-muted-foreground">
                            Thinking...
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto max-w-3xl px-4 py-4">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <Input
              ref={inputRef}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask a question about your documents..."
              disabled={loading}
              className="flex-1 h-11"
            />
            <Button 
              type="submit" 
              disabled={loading || !question.trim()}
              size="icon"
              className="h-11 w-11"
            >
              {loading ? (
                <Spinner className="h-4 w-4" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </form>
        </div>
      </div>
    </div>
  )
}
