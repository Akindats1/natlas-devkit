import { NAtlasError, type ChatMessage, type Language } from "@akindats/natlas";
import { natlas } from "../../lib";

export const runtime = "nodejs";

export async function POST(req: Request) {
  const { messages, replyIn } = (await req.json()) as { messages: ChatMessage[]; replyIn?: Language };
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      try {
        for await (const token of natlas.stream(messages, { replyIn, signal: req.signal })) {
          controller.enqueue(encoder.encode(token));
        }
      } catch (e) {
        const msg = e instanceof NAtlasError ? e.message : "Something went wrong";
        controller.enqueue(encoder.encode(`\n\n⚠️ ${msg}`));
      }
      controller.close();
    },
  });
  return new Response(stream, { headers: { "Content-Type": "text/plain; charset=utf-8" } });
}
