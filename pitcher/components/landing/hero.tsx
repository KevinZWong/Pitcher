import { ArrowDownRight, Presentation, GitBranch, Mic2 } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const Hero1 = () => {
  return (
    <section className="py-32">
      <div className="container">
        <div className="grid items-center gap-8 lg:grid-cols-2">
          <div className="flex flex-col items-center text-center lg:items-start lg:text-left">
            <Badge variant="outline" className="animate-pulse">
              AI-Powered Presentations
              <ArrowDownRight className="ml-2 size-4" />
            </Badge>
            <h1 className="my-6 text-pretty text-4xl font-bold lg:text-6xl">
              Pitch. Ask. <span className="bg-gradient-to-r from-blue-500 to-violet-500 bg-clip-text text-transparent">Evolve.</span>
            </h1>
            <p className="mb-8 max-w-xl text-muted-foreground lg:text-xl">
              Turn your projects into dynamic presentations that evolve based on audience interaction.
            </p>
            <div className="flex w-full flex-col justify-center gap-2 sm:flex-row lg:justify-start">
              <Button className="w-full sm:w-auto" asChild>
                <a href="/dashboard">Create Your Pitch</a>
              </Button>
              <Button variant="outline" className="w-full sm:w-auto">
                Watch Demo
                <ArrowDownRight className="ml-2 size-4" />
              </Button>
            </div>
            <div className="mt-8 flex flex-wrap justify-center gap-4 text-sm text-muted-foreground lg:justify-start">
              <div className="flex items-center gap-2">
                <GitBranch className="size-4" />
                GitHub Integration
              </div>
              <div className="flex items-center gap-2">
                <Presentation className="size-4" />
                Dynamic Slides
              </div>
              <div className="flex items-center gap-2">
                <Mic2 className="size-4" />
                AI Voice Synthesis
              </div>
            </div>
          </div>
          <img
            src="/images/pitcher-hero.png"
            alt="Pitcher AI presentation platform"
            className="max-h-96 w-full rounded-md object-cover shadow-lg"
          />
        </div>
      </div>
    </section>
  );
};

export default Hero1;
