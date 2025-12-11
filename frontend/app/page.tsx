"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Spinner } from "@/components/ui/spinner"
import { ThemeToggle } from "@/components/theme-toggle"
import { sendChatMessage, type ChatResponse, type SourceChunk } from "@/lib/api"
import Link from "next/link"

interface Message {
  role: "user" | "assistant"
  content: string
  sources?: SourceChunk[]
}

export default function Home() {
  const [question, setQuestion] = useState("")
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)

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
    <div className="min-h-screen p-6 md:p-10">
      <div className="mx-auto max-w-4xl">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">RAG Chat Interface</h1>
            <p className="text-muted-foreground">
              Ask questions about your documents
            </p>
          </div>
          <div className="flex items-center gap-3">
            <ThemeToggle />
            <Link href="/login">
              <Button variant="outline">Admin Login</Button>
            </Link>
          </div>
        </div>

        {/* Chat Messages */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Chat</CardTitle>
            <CardDescription>
              Start a conversation with your documents
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 min-h-[400px] max-h-[600px] overflow-y-auto mb-4">
              {messages.length === 0 ? (
                <div className="flex items-center justify-center h-full text-muted-foreground">
                  <p>No messages yet. Ask a question to get started!</p>
                </div>
              ) : (
                messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${
                      message.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg p-4 ${
                        message.role === "user"
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted"
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{message.content}</p>
                      {message.sources && message.sources.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-border">
                          <p className="text-xs font-semibold mb-2">Sources:</p>
                          <div className="space-y-2">
                            {message.sources.map((source, idx) => (
                              <div
                                key={idx}
                                className="text-xs p-2 bg-background rounded border"
                              >
                                <p className="line-clamp-3">{source.content}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-muted rounded-lg p-4">
                    <p>Thinking...</p>
                  </div>
                </div>
              )}
            </div>

            {/* Input Form */}
            <form onSubmit={handleSubmit} className="flex gap-2">
              <Input
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask a question about your documents..."
                disabled={loading}
                className="flex-1"
              />
              <Button type="submit" disabled={loading || !question.trim()}>
                {loading ? (
                  <>
                    <Spinner className="mr-2" />
                    Sending...
                  </>
                ) : (
                  "Send"
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
