"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
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
import {
  getCurrentUser,
  removeAuthToken,
  uploadDocument,
  type UserResponse,
  type UploadResponse,
} from "@/lib/api"

export default function AdminDashboard() {
  const router = useRouter()
  const [user, setUser] = useState<UserResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState<string | null>(null)
  const [file, setFile] = useState<File | null>(null)

  const checkAuth = async () => {
    try {
      const currentUser = await getCurrentUser()
      if (!currentUser.is_admin) {
        router.push("/login")
        return
      }
      setUser(currentUser)
    } catch {
      router.push("/login")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    checkAuth()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleLogout = () => {
    removeAuthToken()
    router.push("/login")
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setUploadStatus(null)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setUploadStatus("Please select a file")
      return
    }

    setUploading(true)
    setUploadStatus(null)

    try {
      const result: UploadResponse = await uploadDocument(file)
      setUploadStatus(
        `Successfully uploaded "${result.filename}". Created ${result.chunks} chunks in collection "${result.collection}".`
      )
      setFile(null)
      // Reset file input
      const fileInput = document.getElementById("file-upload") as HTMLInputElement
      if (fileInput) fileInput.value = ""
    } catch (error) {
      setUploadStatus(
        error instanceof Error ? error.message : "Upload failed"
      )
    } finally {
      setUploading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div>Loading...</div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen p-6 md:p-10">
      <div className="mx-auto max-w-4xl">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Admin Dashboard</h1>
            <p className="text-muted-foreground">Manage RAG pipeline documents</p>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">{user.email}</span>
            <ThemeToggle />
            <Button variant="outline" onClick={handleLogout}>
              Logout
            </Button>
          </div>
        </div>

        <div className="space-y-6">
          {/* Document Upload */}
          <Card>
            <CardHeader>
              <CardTitle>Upload Document</CardTitle>
              <CardDescription>
                Upload a PDF or text file to be indexed in the RAG pipeline
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Input
                  id="file-upload"
                  type="file"
                  accept=".pdf,.txt"
                  onChange={handleFileChange}
                  disabled={uploading}
                />
                {file && (
                  <p className="mt-2 text-sm text-muted-foreground">
                    Selected: {file.name} ({(file.size / 1024).toFixed(2)} KB)
                  </p>
                )}
              </div>
              <Button onClick={handleUpload} disabled={!file || uploading}>
                {uploading ? (
                  <>
                    <Spinner className="mr-2" />
                    Uploading...
                  </>
                ) : (
                  "Upload Document"
                )}
              </Button>
              {uploadStatus && (
                <div
                  className={`rounded-md p-3 text-sm ${
                    uploadStatus.includes("Successfully")
                      ? "bg-green-50 text-green-900 dark:bg-green-950 dark:text-green-100"
                      : "bg-destructive/15 text-destructive"
                  }`}
                >
                  {uploadStatus}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Pipeline Information */}
          <Card>
            <CardHeader>
              <CardTitle>RAG Pipeline Status</CardTitle>
              <CardDescription>
                Monitor the performance and status of the RAG pipeline
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Status</span>
                  <span className="font-medium text-green-600">Active</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Collection</span>
                  <span className="font-medium">bplus-rag</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Vector Store</span>
                  <span className="font-medium">ChromaDB</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Navigation */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-4">
                <Button
                  variant="outline"
                  onClick={() => router.push("/")}
                >
                  View Chat Interface
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

