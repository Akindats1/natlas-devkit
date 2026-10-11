import { NAtlas } from "@akindats/natlas";

const natlas = new NAtlas({ baseUrl: "http://localhost:8000" });

// 1. One question, one answer
console.log(await natlas.ask("What is the capital of Lagos State?"));

// 2. Force a reply in Hausa
console.log(await natlas.ask("Explain what a budget is", { replyIn: "ha" }));

// 3. Translate
console.log((await natlas.translate("Your order has been delivered", "ig")).translation);

// 4. Stream token by token
for await (const token of natlas.stream("Tell me a short story about Lagos traffic")) {
  process.stdout.write(token);
}
