"use client"

import { useUser } from "@/hooks/use-user";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus, GitBranch, Clock, Presentation } from "lucide-react";
import Link from "next/link";

interface ProjectCard {
  id: string;
  title: string;
  description: string;
  lastModified: string;
  slides: number;
}

// Mock data - replace with actual data fetching
const mockProjects: ProjectCard[] = [
  {
    id: "1",
    title: "E-Commerce Platform",
    description: "React and Node.js based marketplace solution",
    lastModified: "2 hours ago",
    slides: 12
  },
  {
    id: "2",
    title: "Mobile Banking App",
    description: "Flutter-based financial services application",
    lastModified: "Yesterday",
    slides: 8
  },
  {
    id: "3",
    title: "AI Chat Assistant",
    description: "Python-based conversational AI system",
    lastModified: "3 days ago",
    slides: 15
  }
];

export default function Dashboard() {
  const user = useUser()

  return (
    <div className="h-full w-full">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-2xl font-semibold mb-1">Welcome</h2>
          <p className="text-sm text-muted-foreground">
            Create and manage your project presentations
          </p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" /> New Project
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Project Cards */}
        {mockProjects.map((project) => (
          <Link href={`/dashboard/projects/${project.id}`} key={project.id} className="h-[320px]">
            <Card className="hover:shadow-md transition-all cursor-pointer hover:border-primary/50 h-full flex flex-col">
              <CardHeader>
                <CardTitle className="flex justify-between items-start">
                  <span>{project.title}</span>
                  <GitBranch className="h-5 w-5 text-muted-foreground" />
                </CardTitle>
                <p className="text-sm text-muted-foreground">{project.description}</p>
              </CardHeader>
              
              {/* Slide Preview */}
              <CardContent className="flex-1">
                <div className="w-full h-32 bg-muted/30 rounded-md flex items-center justify-center">
                  <Presentation className="h-8 w-8 text-muted-foreground/50" />
                </div>
              </CardContent>

              <CardFooter className="flex justify-between text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                  <Presentation className="h-4 w-4" />
                  <span>{project.slides} slides</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  <span>{project.lastModified}</span>
                </div>
              </CardFooter>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
