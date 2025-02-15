import {
    DollarSign,
    MessagesSquare,
    PersonStanding,
    Timer,
    Zap,
    ZoomIn,
    GitBranch,
    Presentation,
    Mic2,
    Bot,
    FileSearch,
    BrainCircuit,
  } from "lucide-react";
  
  const features = [
    {
      title: "GitHub Integration",
      description:
        "Connect your GitHub repository and let Pitcher analyze your codebase to create comprehensive presentations automatically.",
      icon: <GitBranch className="size-4 md:size-6" />,
    },
    {
      title: "AI Slide Generation",
      description:
        "Transform your project documentation and code into professional, visually appealing slides with just one click.",
      icon: <Presentation className="size-4 md:size-6" />,
    },
    {
      title: "AI Voice Synthesis",
      description:
        "Generate natural-sounding voiceovers for your presentations using advanced AI voice models.",
      icon: <Mic2 className="size-4 md:size-6" />,
    },
    {
      title: "Interactive Q&A",
      description:
        "Let AI handle audience questions about your project in real-time, providing accurate and contextual responses.",
      icon: <Bot className="size-4 md:size-6" />,
    },
    {
      title: "Document Analysis",
      description:
        "Automatically process project documentation, READMEs, and Drive files to extract key information for your pitch.",
      icon: <FileSearch className="size-4 md:size-6" />,
    },
    {
      title: "Dynamic Adaptation",
      description:
        "Create additional slides on the fly and adapt your presentation based on audience interests and questions.",
      icon: <BrainCircuit className="size-4 md:size-6" />,
    },
  ];
  
  const Feature17 = () => {
    return (
      <section className="py-32">
        <div className="container mx-auto max-w-screen-xl">
          <p className="mb-4 text-xs text-muted-foreground md:pl-5">Features</p>
          <h2 className="text-3xl font-medium md:pl-5 lg:text-4xl">
            Our Core Features
          </h2>
          <div className="mx-auto mt-14 grid gap-x-20 gap-y-8 md:grid-cols-2 md:gap-y-6 lg:mt-20">
            {features.map((feature, idx) => (
              <div className="flex gap-6 rounded-lg md:block md:p-5" key={idx}>
                <span className="mb-8 flex size-10 shrink-0 items-center justify-center rounded-full bg-accent md:size-12">
                  {feature.icon}
                </span>
                <div>
                  <h3 className="font-medium md:mb-2 md:text-xl">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-muted-foreground md:text-base">
                    {feature.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    );
  };
  
  export default Feature17;
  