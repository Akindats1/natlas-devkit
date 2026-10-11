# N-ATLAS Dev Kit

**Add Nigeria's own AI to any app in 5 minutes.**

N-ATLAS is Nigeria's open-source multilingual large language model (English, Hausa, Igbo, Yoruba). It is powerful, but today a developer who wants to use it must download 16 GB of weights, write Python inference code, and build their own API. There is no hosted endpoint, no SDK, and no starter app.

The **N-ATLAS Dev Kit** removes that barrier:

| Part | What it does |
|---|---|
| [`server/`](server) | Runs N-ATLAS behind an **OpenAI-compatible API**. Any app already built for OpenAI switches to N-ATLAS by changing one URL. Runs on a laptop (CPU), Docker, or free Google Colab GPU. |
| [`sdk-typescript/`](sdk-typescript) | `natlas` npm package. Zero dependencies. Chat, streaming, translation, language detection. Node 18+, browsers, Next.js. |
| [`sdk-dotnet/`](sdk-dotnet) | `NAtlas` .NET package. Works in .NET 8 **and** .NET Framework apps, including desktop software and Revit/AutoCAD plugins. |
| [`starter-nextjs/`](starter-nextjs) | A working multilingual chat app. Clone it, set one environment variable, ship. |

> N-ATLaS is an initiative of the Federal Ministry of Communications, Innovation and Digital Economy, and powered by Awarri Technologies.

---

## Quickstart (5 minutes)

### 1. Start the server

**Option A — Laptop (CPU, ~6 GB free RAM):**

```bash
cd server
pip install -r requirements.txt
python -m natlas_server          # downloads the 4.9 GB Q4 model on first run
```

**Option B — Docker:**

```bash
cd server
docker compose up
```

**Option C — Free GPU on Google Colab:** open [`server/natlas_colab.ipynb`](server/natlas_colab.ipynb), run all cells, copy the public URL.

**Option D — Try the API without a model (mock mode):**

```bash
NATLAS_BACKEND=mock python -m natlas_server
```

Open http://localhost:8000/docs to see and try every endpoint.

### 2. Call it

**curl**

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Explain inflation simply"}],"reply_language":"ha"}'
```

**TypeScript**

```ts
import { NAtlas } from "natlas";
const natlas = new NAtlas({ baseUrl: "http://localhost:8000" });

await natlas.ask("Explain inflation simply", { replyIn: "ha" });
await natlas.translate("Your order has been delivered", "ig");
for await (const t of natlas.stream("Tell me about Lagos")) process.stdout.write(t);
```

**C# / .NET**

```csharp
using NAtlas;
using var natlas = new NAtlasClient("http://localhost:8000");

var answer = await natlas.AskAsync("Explain inflation simply", new ChatOptions { ReplyIn = Language.Hausa });
var yo = await natlas.TranslateAsync("Concrete pouring starts at 7am", Language.Yoruba);
```

**Existing OpenAI code (Python, JS, anything)** — change only the base URL:

```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8000/v1", api_key="anything")
client.chat.completions.create(model="n-atlas", messages=[{"role": "user", "content": "Sannu"}])
```

### 3. Or start from the Next.js app

```bash
cd sdk-typescript && npm install && npm run build
cd ../starter-nextjs && cp .env.example .env.local && npm install && npm run dev
```

---

## API reference

| Method | Path | Purpose |
|---|---|---|
| POST | `/v1/chat/completions` | OpenAI-compatible chat. Supports `stream: true`. Extra field `reply_language` (`en`/`ha`/`ig`/`yo`) forces the reply language. |
| POST | `/v1/translate` | `{ text, target, source? }` → `{ translation }` |
| POST | `/v1/detect-language` | Fast heuristic guess of `en`/`ha`/`ig`/`yo` |
| GET | `/v1/models` | Lists `n-atlas` |
| GET | `/v1/stats` | Anonymous usage summary (requests per client, language, latency) |
| GET | `/health` | Liveness check |

Every response carries the header `X-Powered-By: N-ATLaS (Awarri Technologies / FMCIDE)`.

## Configuration (server environment variables)

| Variable | Default | Meaning |
|---|---|---|
| `NATLAS_BACKEND` | `llamacpp` | `llamacpp` (GGUF, CPU/GPU), `transformers` (official weights, GPU), `mock` (no model) |
| `NATLAS_GGUF_REPO` | `tosinamuda/N-ATLaS-GGUF` | Quantized model repository |
| `NATLAS_GGUF_FILE` | `N-ATLaS-GGUF-Q4_K_M.gguf` | Q4 (4.9 GB) default; Q8 (8.5 GB) for higher quality |
| `NATLAS_MODEL_PATH` | — | Use a local `.gguf` file instead of downloading |
| `NATLAS_GPU_LAYERS` | `0` | `-1` = all layers on GPU |
| `NATLAS_HF_MODEL` | `NCAIR1/N-ATLaS` | Official weights for the `transformers` backend |
| `NATLAS_LOAD_4BIT` | — | `1` = load official weights in 4-bit (fits a free T4) |
| `NATLAS_API_KEY` | — | If set, clients must send `Authorization: Bearer <key>` |
| `NATLAS_LOG` | `usage.jsonl` | Anonymous usage log path (no message text is stored) |

## Tests

```bash
# server
cd server && pip install fastapi uvicorn httpx pytest && pytest
# TypeScript SDK (needs a running server, mock mode is fine)
NATLAS_BACKEND=mock python -m natlas_server &
cd sdk-typescript && npm install && npm run build && npm test
# .NET SDK demo
cd sdk-dotnet && dotnet run --project samples/NAtlas.Demo
```

## Known limitations

These come from the N-ATLAS model itself and are passed through honestly:

- Yoruba quality is lower than English, Hausa and Igbo (2.69/5 in NCAIR's own human evaluation).
- Context is limited to about 8,000 tokens.
- On a laptop CPU, replies take several seconds; use a GPU (Colab/cloud) for real-time apps.
- `detect-language` is a fast heuristic, not a trained classifier. It is meant for routing, not linguistics.
- One model instance serves one request at a time; run more instances behind a load balancer to scale.

## Licence

- **Dev Kit code:** MIT (see [LICENSE](LICENSE)).
- **N-ATLAS model:** governed by the N-ATLaS Terms of Use (Awarri Technologies / FMCIDE): free for research, education, civic and community use; up to 1,000 active end-users without a commercial licence; attribution required.

Apps built with this kit must follow the N-ATLaS acceptable-use terms:

| Permitted (including but not limited to) | Prohibited (including but not limited to) |
|---|---|
| Academic and non-profit research | Surveillance or unlawful monitoring |
| Accessibility for persons with disabilities | Discriminatory profiling or exclusionary practices |
| Language and cultural preservation | Disinformation, impersonation, or synthetic fraud |
| Civic technology and public-benefit applications | Military, intelligence, or weaponised deployment |
| Education, training, and community innovation | Exploitative, harmful, or unlawful applications |

Built by **KS Digital Innovations**, Lagos.
