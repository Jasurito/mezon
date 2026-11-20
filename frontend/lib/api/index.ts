import { liveApi } from "./live";
import { mockApi } from "./mock";
import type { Api } from "./types";

/** "mock" until the backend is deployed next to the frontend; flip with NEXT_PUBLIC_API_MODE=live. */
export const API_MODE = process.env.NEXT_PUBLIC_API_MODE === "live" ? "live" : "mock";
export const api: Api = API_MODE === "live" ? liveApi : mockApi;
export * from "./types";
