# N-ATLAS Dev Kit — Beta Tester Guide (15–20 minutes)

Thank you for testing! N-ATLAS is Nigeria's own AI model (English, Hausa, Igbo, Yoruba). This kit lets developers use it like the OpenAI API.

## Pick ONE way to connect

**Easy (no setup):** use the shared server. It runs the real N-ATLAS model on a laptop GPU, so replies take a few seconds.

```bash
# macOS / Linux / Git Bash
export NATLAS_BASE_URL=https://exalted-herbal-bulge.ngrok-free.dev
export NATLAS_API_KEY=<key Akindats sends you privately>

# Windows PowerShell
$env:NATLAS_BASE_URL = "https://exalted-herbal-bulge.ngrok-free.dev"
$env:NATLAS_API_KEY  = "<key Akindats sends you privately>"
```

Opening the URL in a browser (for example `/docs`) first shows an ngrok warning page. Click **Visit Site**. Code and curl are not affected.

**Full (your own machine, needs ~6 GB free RAM and Python 3.10–3.12):**

```bash
git clone https://github.com/Akindats1/natlas-devkit.git
cd natlas-devkit/server
pip install -r requirements.txt --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
python -m natlas_server
```

## Tasks

**0. Try it in your browser first (2 minutes)**

Open **https://exalted-herbal-bulge.ngrok-free.dev/?tester=YOURNAME** (put your first name at the end, so the server log credits your requests), click **Visit Site**, paste the API key at the top, and ask something in Hausa, Igbo or Yorùbá. Leave **Reply in** on **Auto** to get answers in the language you write. The **Build with it** panel shows the code for your request.

**1. Check it's alive**

```bash
curl $NATLAS_BASE_URL/health
```

**2. Ask something in a Nigerian language** (use your own question)

```bash
curl $NATLAS_BASE_URL/v1/chat/completions \
  -H "Authorization: Bearer $NATLAS_API_KEY" -H "Content-Type: application/json" \
  -H "X-Client-Name: tester-YOURNAME" \
  -d '{"messages":[{"role":"user","content":"YOUR QUESTION"}],"reply_language":"ha"}'
```

**3. Use an SDK in a tiny script of your own**

TypeScript (Node 18+): run `npm install @akindats/natlas`, then save this as `test.mjs` and run `node test.mjs`:

```ts
import { NAtlas } from "@akindats/natlas";
const natlas = new NAtlas({ clientName: "tester-YOURNAME" }); // reads NATLAS_BASE_URL / NATLAS_API_KEY
console.log(await natlas.ask("YOUR QUESTION", { replyIn: "ig" }));
```

or C# (.NET 8): clone the repo, then in your own console project run `dotnet add reference <path-to>/natlas-devkit/sdk-dotnet/src/NAtlas/NAtlas.csproj`:

```csharp
using var natlas = new NAtlas.NAtlasClient(clientName: "tester-YOURNAME");
Console.WriteLine(await natlas.AskAsync("YOUR QUESTION"));
```

**4. (Optional) Run the Next.js starter** — see `starter-nextjs/` in the README.

## Feedback form (reply by email/WhatsApp)

1. Full name, role, organisation:
2. Your OS and machine (CPU/GPU):
3. Which way did you connect (shared server / your own machine)?
4. Which SDK did you use (TypeScript / .NET / curl only)?
5. How many minutes from start to your first N-ATLAS reply?
6. Which languages did you try?
7. Ease of setup, 1 (hard) to 5 (very easy):
8. What worked well?
9. What broke or confused you?
10. Would you use this in a real project? Why / why not?
11. Do you agree to your name and feedback being included in the NAIC 2026 submission? (yes/no)

Thank you! 🙏
