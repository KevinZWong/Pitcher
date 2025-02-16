"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { useToast } from "@/components/ui/use-toast";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useUser } from "@/hooks/use-user";
import router from "next/router";

const formSchema = z.object({
  githubLink: z.string().url({
    message: "Please enter a valid GitHub URL.",
  }),
  driveLink: z
    .string()
    .url({
      message: "Please enter a valid Google Drive URL.",
    })
    .optional(),
  prompt: z.string().min(1, {
    message: "Please enter presentation specifications.",
  }),
});

export default function CreateProjectPage() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      githubLink: "",
      driveLink: "",
      prompt: "",
    },
  });

  const { toast } = useToast();

  async function onSubmit(values: z.infer<typeof formSchema>) {
    try {
      /* Temporary test with local file
      const newWindow = window.open('', '_blank', 'width=800,height=600');
      if (!newWindow) throw new Error('Popup blocked');
      
      newWindow.document.write(`
        <html>
          <body style="margin:0">
            <iframe id="presentation" src="/slides.html" 
              style="width:100vw;height:100vh;border:none;">
            </iframe>
          </body>
          <script>
            let currentSlide = 0;
            
            async function checkStatus() {
              try {
                const status = 'Y'; // Hardcoded for testing
                if (status.includes('Y')) {
                  const iframe = document.getElementById('presentation');
                  const rightArrowEvent = new KeyboardEvent('keydown', {
                    key: 'ArrowRight',
                    keyCode: 39,
                    which: 39,
                    bubbles: true
                  });
                  iframe.contentWindow.document.dispatchEvent(rightArrowEvent);
                  currentSlide++;
                }
              } catch (error) {
                console.error('Status check failed:', error);
              }
              setTimeout(checkStatus, 1000); // Poll every second
            }
            
            checkStatus();
          </script>
        </html>
      `);
      newWindow.document.close();
      */

      const response = await fetch("http://127.0.0.1:5000/api/projects", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: values.prompt,
          githubUrl: values.githubLink,
          driveUrl: values.driveLink,
        }),
      });

      if (!response.ok) throw new Error("Failed to create project");

      const data = await response.json();
      const newWindow = window.open("", "_blank", "width=800,height=600");
      if (!newWindow) throw new Error("Popup blocked");

      newWindow.document.write(`
        <html>
          <body style="margin:0">
            <iframe id="presentation" src="/presentation.html" 
              style="width:100vw;height:100vh;border:none;">
            </iframe>
          </body>
          <script>
            document.addEventListener('DOMContentLoaded', () => {
              const fullscreenEvent = new KeyboardEvent('keydown', {
                key: 'f',
                keyCode: 70,
                which: 70,
                bubbles: true
              });
              document.getElementById('presentation').contentWindow.document.dispatchEvent(fullscreenEvent);
            });

            let currentSlide = 0;
            
            async function checkStatus() {
              try {
                const status = await fetch('/api/presentation-status').then(r => r.text());
                if (status.includes('Y')) {
                  const iframe = document.getElementById('presentation');
                  const rightArrowEvent = new KeyboardEvent('keydown', {
                    key: 'ArrowRight',
                    keyCode: 39,
                    which: 39,
                    bubbles: true
                  });
                  iframe.contentWindow.document.dispatchEvent(rightArrowEvent);
                  currentSlide++;
                }
              } catch (error) {
                console.error('Status check failed:', error);
              }
              setTimeout(checkStatus, 1000); // Poll every second
            }
            
            checkStatus();
          </script>
        </html>
      `);
      newWindow.document.close();

      toast({
        title: "Project created",
        description: "Your presentation has been generated successfully.",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: error.message || "An error occurred while creating the project.",
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
            Add a new project by providing the GitHub repository link and
            optional files.
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
                      <Input
                        placeholder="https://github.com/username/repo"
                        {...field}
                      />
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
                      <Input
                        placeholder="https://drive.google.com/..."
                        {...field}
                      />
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
                      console.log(e.target.files);
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
  );
}
