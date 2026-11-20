"use client";
import { useParams } from "next/navigation";
import { PlayScreen } from "@/components/play/play-screen";

export default function PlayPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  return <PlayScreen sessionId={sessionId} />;
}
