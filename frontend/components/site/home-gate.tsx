"use client";
import type { ReactNode } from "react";
import { useUser } from "@/store/user";

/**
 * Home page: a descriptive page for guests (what Mezon is, for whom, how it works), the case desk for signed-in
 * users. The server renders the guest page (search engines, first visit); a signed-in user is switched to the desk
 * once the session is known.
 */
export function HomeGate({ guest, member }: { guest: ReactNode; member: ReactNode }) {
  const { ready, account } = useUser();
  return <>{ready && account ? member : guest}</>;
}
