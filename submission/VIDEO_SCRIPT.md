# Video Script — 4 minutes

**Setup before recording:** server running with the REAL model (`llamacpp` or Colab GPU), terminal with large font, browser tabs open: `/docs`, the Next.js starter, VS Code with the two SDK examples. Record with OBS or Loom. Speak slowly and clearly.

---

### 0:00 – 0:25 | The problem
**Show:** N-ATLAS Hugging Face page.
**Say:**
"N-ATLAS is Nigeria's own multilingual AI model. But today, if a developer wants to use it, they have to download 16 gigabytes, write Python inference code and build their own API. There's no SDK and no starter app. Most developers stop there."

### 0:25 – 0:45 | The solution
**Show:** the README table.
**Say:**
"The N-ATLAS Dev Kit fixes that. It has four parts: an OpenAI-compatible server, a TypeScript SDK, a .NET SDK, and a ready-to-use Next.js app."

### 0:45 – 1:30 | Start the server
**Show:** terminal: `python -m natlas_server`, then `curl localhost:8000/health` showing the real backend.
**Say:**
"One command starts N-ATLAS on an ordinary laptop, using a 5-gigabyte quantized version. It also runs in Docker or on a free Colab GPU. Here's the health check: the real N-ATLAS model is loaded."
**Show:** `/docs` page in browser.
"Every endpoint is documented and testable here."

### 1:30 – 2:10 | OpenAI compatibility
**Show:** Python OpenAI client with only `base_url` changed, asking a Hausa question; the answer appears.
**Say:**
"This is the key feature. Any app built for OpenAI can switch to Nigeria's model by changing one line: the base URL. Here's the standard OpenAI library answering in Hausa, powered by N-ATLAS."

### 2:10 – 2:50 | The SDKs
**Show:** run `examples/quickstart.mjs` (ask, replyIn Hausa, translate to Igbo, streaming).
**Say:**
"For JavaScript developers: `npm install natlas`. Ask a question, force replies in Hausa, translate to Igbo, or stream tokens live."
**Show:** run the .NET demo.
"And for .NET developers, including desktop and engineering software like Revit plugins, the same features in C#."

### 2:50 – 3:25 | The starter app
**Show:** Next.js app: pick Igbo, ask a question, reply streams in.
**Say:**
"The Next.js starter is a complete multilingual chat app. Users ask in any language and choose the reply language. A developer can clone this and ship a Nigerian-language product today."

### 3:25 – 3:50 | Real-world validation
**Show:** `/v1/stats` output + tester feedback.
**Say:**
"We tested with [number] external developers. [Name] got their first reply in [X] minutes. Here are the real usage numbers from the server log."

### 3:50 – 4:10 | Impact & close
**Say:**
"Every app built with this kit puts N-ATLAS in front of more Nigerians. Our goal is simple: make building with Nigeria's AI as easy as building with any global AI. N-ATLAS is an initiative of the Federal Ministry of Communications, Innovation and Digital Economy, powered by Awarri Technologies. Thank you."
