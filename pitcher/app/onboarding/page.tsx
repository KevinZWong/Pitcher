'use client'

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useMutation } from "convex/react"
import { api } from "@/convex/_generated/api"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Loader2, User } from "lucide-react"
import { useUser } from "@/hooks/use-user"
import { redirect } from "next/navigation";


export default function Onboarding() {
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()
  const user = useUser()
  const updateUser = useMutation(api.users.update)

  if (user && user.hasCompletedOnboarding) {
    redirect('/dashboard')
  }

  return (
    <div className="flex min-h-screen items-center justify-center">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Welcome!</CardTitle>
          <CardDescription>Let's get to know you better</CardDescription>
        </CardHeader>
        <form
          onSubmit={async (event) => {
            event.preventDefault()
            setIsLoading(true)
            try {
              const formData = new FormData(event.currentTarget)
              await updateUser({
                name: formData.get("name") as string,
                email: user?.email, // Preserve existing email if any
                hasCompletedOnboarding: true
              })
              router.push("/dashboard")
            } finally {
              setIsLoading(false)
            }
          }}
        >
          <CardContent>
            <div className="relative">
              <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input 
                name="name" 
                placeholder="Your name" 
                className="pl-9"
                disabled={isLoading}
                required
              />
            </div>
          </CardContent>
          <CardFooter>
            <Button 
              type="submit" 
              className="w-full"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                "Continue to dashboard"
              )}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  )
}
