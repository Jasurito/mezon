import { SiteFooter, SiteHeader } from "@/components/site/site-header";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <SiteHeader />
      <main id="main" className="mx-auto w-full max-w-6xl px-4 pt-10 sm:px-6">{children}</main>
      <SiteFooter />
    </>
  );
}
