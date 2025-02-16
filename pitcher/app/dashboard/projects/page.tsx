"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { useToast } from "@/components/ui/use-toast"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { useUser } from "@/hooks/use-user"
import router from "next/router"

const formSchema = z.object({
  githubLink: z.string().url({
    message: "Please enter a valid GitHub URL.",
  }),
  driveLink: z.string().url({
    message: "Please enter a valid Google Drive URL.",
  }).optional(),
  prompt: z.string().min(1, {
    message: "Please enter presentation specifications.",
  }),
})

export default function CreateProjectPage() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      githubLink: "",
      driveLink: "",
      prompt: "",
    },
  })

  const { toast } = useToast()
  
  async function onSubmit(values: z.infer<typeof formSchema>) {
    try {
      const response = await fetch('/api/projects', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(values),
      });
      
      if (!response.ok) throw new Error('Failed to create project');
      
      toast({
        title: "Project created",
        description: "Your project has been created successfully.",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create project. Please try again.",
        variant: "destructive",
      });
    }
  }

  return (
    <div>
      <div className="max-w-xl p-4">
        <div className="mb-4">
          <h2 className="text-xl font-semibold mb-1">Create New Project</h2>
          <p className="text-sm text-muted-foreground">
            Add a new project by providing the GitHub repository link and optional files.
          </p>
        </div>
        <div>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="githubLink"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>GitHub Repository URL</FormLabel>
                    <FormControl>
                      <Input placeholder="https://github.com/username/repo" {...field} />
                    </FormControl>
                    <FormDescription>
                      The link to your GitHub repository
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="driveLink"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Google Drive Link (Optional)</FormLabel>
                    <FormControl>
                      <Input placeholder="https://drive.google.com/..." {...field} />
                    </FormControl>
                    <FormDescription>
                      Optional: Link to your Google Drive folder or file
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormItem>
                <FormLabel>Or Upload Files</FormLabel>
                <FormControl>
                  <Input 
                    type="file" 
                    multiple 
                    onChange={(e) => {
                      console.log(e.target.files)
                    }} 
                  />
                </FormControl>
                <FormDescription>
                  Upload relevant project files directly
                </FormDescription>
              </FormItem>
              <FormField
                control={form.control}
                name="prompt"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Presentation Specifications</FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="Enter any specific requirements for the presentation..." 
                        {...field} 
                      />
                    </FormControl>
                    <FormDescription>
                      Describe how you want your presentation to be generated
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit">Create Project</Button>
            </form>
          </Form>
        </div>
      </div>
    </div>
  )
}
