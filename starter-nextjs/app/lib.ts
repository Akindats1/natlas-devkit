import { NAtlas } from "natlas";

// Server-only: keeps NATLAS_API_KEY out of the browser.
export const natlas = new NAtlas({
  baseUrl: process.env.NATLAS_BASE_URL,
  apiKey: process.env.NATLAS_API_KEY,
  clientName: process.env.NATLAS_CLIENT_NAME ?? "nextjs-starter",
});
