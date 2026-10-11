# natlas

TypeScript SDK for **N-ATLAS**, Nigeria's multilingual LLM (English, Hausa, Igbo, Yoruba). Zero dependencies. Node 18+, browsers, Next.js.

```bash
npm install @akindats/natlas
```

```ts
import { NAtlas } from "@akindats/natlas";
const natlas = new NAtlas({ baseUrl: "http://localhost:8000" }); // or NATLAS_BASE_URL env

await natlas.ask("Explain inflation simply", { replyIn: "ha" });      // force Hausa reply
await natlas.chat([{ role: "user", content: "Kedu?" }]);              // full chat
for await (const t of natlas.stream("Tell me about Lagos")) process.stdout.write(t);
await natlas.translate("Your order has arrived", "yo");
await natlas.detectLanguage("Kedu ka ị mere?");                       // { language: "ig", ... }
```

Needs an N-ATLAS server: see the [Dev Kit README](../README.md).

> N-ATLaS is an initiative of the Federal Ministry of Communications, Innovation and Digital Economy, and powered by Awarri Technologies.
