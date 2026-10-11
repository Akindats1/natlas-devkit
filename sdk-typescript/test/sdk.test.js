// Runs against a live server: NATLAS_BACKEND=mock python -m natlas_server
import { test } from "node:test";
import assert from "node:assert/strict";
import { NAtlas, NAtlasError } from "../dist/index.js";

const natlas = new NAtlas({ baseUrl: process.env.NATLAS_BASE_URL ?? "http://localhost:8000", clientName: "sdk-test" });

test("health", async () => {
  assert.equal((await natlas.health()).status, "ok");
});

test("chat + ask", async () => {
  const r = await natlas.chat([{ role: "user", content: "Kedu?" }]);
  assert.ok(r.text.length > 0);
  assert.ok(typeof (await natlas.ask("Sannu", { replyIn: "ha" })) === "string");
});

test("stream", async () => {
  let out = "";
  for await (const t of natlas.stream("Bawo ni")) out += t;
  assert.ok(out.length > 0);
});

test("translate + detect", async () => {
  const t = await natlas.translate("Good morning", "yo");
  assert.ok("translation" in t);
  assert.equal((await natlas.detectLanguage("Kedu ka ị mere?")).language, "ig");
});

test("bad language -> NAtlasError 400", async () => {
  await assert.rejects(() => natlas.ask("x", { replyIn: "fr" }), (e) => e instanceof NAtlasError && e.status === 400);
});

test("unreachable server -> friendly error", async () => {
  const dead = new NAtlas({ baseUrl: "http://127.0.0.1:1" });
  await assert.rejects(() => dead.health(), /Could not reach N-ATLAS/);
});
