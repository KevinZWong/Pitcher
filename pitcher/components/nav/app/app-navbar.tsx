import React from "react";
import {
  Bell,
  MessageSquare,
  Github,
  BookOpen,
  HelpCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
interface NavbarProps {
  path: string;
}
export function Navbar({ path }: NavbarProps) {
  const getPageTitle = (path: string) => {
    const segments = path.split("/").filter(Boolean);
    if (segments.length === 0) return "Dashboard";
    return segments
      .map((s) => s.charAt(0).toUpperCase() + s.slice(1))
      .join(" / ");
  };
  return (
    <header className="h-12 border-b flex items-center bg-background sticky top-0 z-20 w-full">
      <div className="flex items-center justify-between w-full px-3">
        <div className="text-base font-medium pl-12">{getPageTitle(path)}</div>
        <div className="flex items-center gap-1.5">
          <div className="flex items-center gap-1.5">
            <Button variant="outline" size="sm" className="h-7 text-xs px-2.5">
              <Bell className="w-3.5 h-3.5 mr-1" />
              Alerts
            </Button>
            <Button variant="outline" size="sm" className="h-7 text-xs px-2.5">
              <MessageSquare className="w-3.5 h-3.5 mr-1" />
              Chat
            </Button>
          </div>
          <div className="h-5 w-px bg-border mx-1.5" />
          <div className="flex items-center gap-1.5">
            <Button variant="outline" size="sm" className="h-7 text-xs px-2.5">
              <Github className="w-3.5 h-3.5 mr-1" />
              Code
            </Button>
            <Button variant="outline" size="sm" className="h-7 text-xs px-2.5">
              <BookOpen className="w-3.5 h-3.5 mr-1" />
              Docs
            </Button>
            <Button variant="outline" size="sm" className="h-7 text-xs px-2.5">
              <HelpCircle className="w-3.5 h-3.5 mr-1" />
              Help
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
}
