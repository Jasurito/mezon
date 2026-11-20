"use client";
import { useEffect } from "react";
import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { applySettings } from "@/lib/settings";
import { useSettings } from "@/store/settings";
import { useUser } from "@/store/user";
import { LegalPanel } from "./legal-panel";
import { SketchSwitcher } from "./sketch-switcher";

export function Providers({ children }: { children: React.ReactNode }) {
  const init = useUser((s) => s.init);
  useEffect(() => {
    init();
    const s = useSettings.getState(); applySettings({ family: s.family, size: s.size, lineHeight: s.lineHeight, motion: s.motion });
  }, [init]);
  return (
    <TooltipProvider delayDuration={300}>
      {children}
      <LegalPanel />
      <SketchSwitcher />
      <Toaster theme="dark" position="top-center" />
    </TooltipProvider>
  );
}
