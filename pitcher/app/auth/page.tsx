'use client'
import { useAuthActions } from "@convex-dev/auth/react";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  InputOTP,
  InputOTPGroup,
  InputOTPSeparator,
  InputOTPSlot,
} from "@/components/ui/input-otp"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { ArrowRight, Mail, Loader2 } from "lucide-react"

import { Authenticated, Unauthenticated, useQuery } from "convex/react";
import { api } from "@/convex/_generated/api";

export default function Auth() {
  const { signIn } = useAuthActions();
  const [step, setStep] = useState<"signIn" | { email: string }>("signIn");
  const [otp, setOtp] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  return (
    <>
        <div className="flex min-h-screen items-center justify-center">
          <Card className="w-full max-w-md">
            {step === "signIn" ? (
              <>
                <CardHeader>
                  <CardTitle>Welcome back</CardTitle>
                  <CardDescription>Enter your email to sign in to your account</CardDescription>
                </CardHeader>
                <form
                  onSubmit={async (event) => {
                    event.preventDefault();
                    setIsLoading(true);
                    const formData = new FormData(event.currentTarget);
                    setStep({ email: formData.get("email") as string });
                    try {
                      await signIn("resend-otp", formData);
                      // Redirect will be handled by middleware
                    } finally {
                      setIsLoading(false);
                    }
                  }}
                >
                  <CardContent>
                    <div className="relative">
                      <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input 
                        name="email" 
                        placeholder="name@example.com" 
                        type="email"
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
                          Sending code...
                        </>
                      ) : (
                        <>
                          Next
                          <ArrowRight className="ml-2 h-4 w-4" />
                        </>
                      )}
                    </Button>
                  </CardFooter>
                </form>
              </>
            ) : (
              <>
                <CardHeader>
                  <CardTitle>Check your email</CardTitle>
                  <CardDescription>
                    We've sent a code to {step.email}
                  </CardDescription>
                </CardHeader>
                <form
                  onSubmit={async (event) => {
                    event.preventDefault();
                    setIsLoading(true);
                    const formData = new FormData();
                    formData.append("email", step.email);
                    formData.append("code", otp);
                    try {
                      await signIn("resend-otp", formData);
                    } finally {
                      setIsLoading(false);
                    }
                  }}
                >
                  <CardContent>
                    <div className="flex justify-center">
                      <InputOTP
                        value={otp}
                        onChange={setOtp}
                        maxLength={6}
                        disabled={isLoading}
                      >
                        <InputOTPGroup >
                          {Array.from({ length: 6 }).map((_, index) => (
                            <InputOTPSlot key={index} index={index} />
                          ))}
                        </InputOTPGroup>
                      </InputOTP>
                    </div>
                    <p className="text-sm text-muted-foreground text-center mt-4">
                      Didn't receive a code? <Button variant="link" className="p-0 h-auto" onClick={() => setStep("signIn")}>Try again</Button>
                    </p>
                  </CardContent>
                  <CardFooter className="flex-col gap-2">
                    <Button 
                      type="submit" 
                      className="w-full"
                      disabled={isLoading || otp.length !== 6}
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Verifying...
                        </>
                      ) : (
                        <>
                          Verify code
                          <ArrowRight className="ml-2 h-4 w-4" />
                        </>
                      )}
                    </Button>
                    <Button 
                      type="button" 
                      variant="ghost"
                      onClick={() => setStep("signIn")}
                      disabled={isLoading}
                      className="w-full"
                    >
                      Use different email
                    </Button>
                  </CardFooter>
                </form>
              </>
            )}
          </Card>
        </div>
    </>
  );
}
