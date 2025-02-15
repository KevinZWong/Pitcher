import HomeNavbar from "@/components/nav/home/home-navbar";
import HomeFooter from "@/components/nav/home/home-footer";
import { ReactNode } from "react";

export default function SplashPageLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <div>
      <HomeNavbar />
      <main>{children}</main>
      <HomeFooter />
    </div>
  );
}
