# N-ATLAS Dev Kit — Beta Tester Guide (15–20 minutes)

Thank you for testing! N-ATLAS is Nigeria's own AI model (English, Hausa, Igbo, Yoruba). This kit lets developers use it like the OpenAI API, through a REST API, SDKs and a browser playground.

## What you need

- **Server URL:** `https://exalted-herbal-bulge.ngrok-free.dev` (the real N-ATLAS model on the team's GPU; replies take a few seconds)
- **API key:** Akindats sends it to you privately. Every API call needs it as `Authorization: Bearer <key>`; without it the API answers **401 Unauthorized**.
- **REST API reference:** open **https://exalted-herbal-bulge.ngrok-free.dev/docs** in a browser (click **Visit Site**, then **Authorize** and paste the key to try every endpoint live). The full list of endpoints is in the [README](../README.md#api-reference).

In every command below, replace `YOUR_KEY` with your key and `YOURNAME` with your first name.

## Tasks

**0. Try it in your browser (2 minutes)**

Open **https://exalted-herbal-bulge.ngrok-free.dev/?tester=YOURNAME**, click **Visit Site**, paste the API key at the top, and ask something in Hausa, Igbo or Yorùbá. Leave **Reply in** on **Auto** to get answers in the language you write. The **Build with it** panel shows the code for your request.

**1. Check it's alive**

```powershell
# Windows PowerShell
Invoke-RestMethod https://exalted-herbal-bulge.ngrok-free.dev/health -Headers @{ "ngrok-skip-browser-warning" = "1" }
```

```bash
# macOS / Linux / Git Bash
curl https://exalted-herbal-bulge.ngrok-free.dev/health
```

You should see `status: ok` and `backend: llamacpp`.

**2. Call the REST API in a Nigerian language** (use your own question)

```powershell
# Windows PowerShell (one block; paste it all)
$headers = @{ Authorization = "Bearer YOUR_KEY"; "X-Client-Name" = "tester-YOURNAME"; "ngrok-skip-browser-warning" = "1" }
$body = '{"messages":[{"role":"user","content":"Explain inflation simply"}],"reply_language":"ha"}'
$r = Invoke-RestMethod https://exalted-herbal-bulge.ngrok-free.dev/v1/chat/completions -Method Post -Headers $headers -ContentType "application/json" -Body $body
$r.choices[0].message.content
```

```bash
# macOS / Linux / Git Bash
curl https://exalted-herbal-bulge.ngrok-free.dev/v1/chat/completions \
  -H "Authorization: Bearer YOUR_KEY" -H "Content-Type: application/json" \
  -H "X-Client-Name: tester-YOURNAME" \
  -d '{"messages":[{"role":"user","content":"Explain inflation simply"}],"reply_language":"ha"}'
```

On Windows, plain `curl` in PowerShell is not real curl, so use the PowerShell block above (or type `curl.exe` instead of `curl` in Command Prompt). The `ngrok-skip-browser-warning` header matters: PowerShell looks like a web browser to the free ngrok tunnel, which otherwise returns its "Visit Site" warning page (`ERR_NGROK_6024`) instead of the API's answer.

**3. Use the TypeScript SDK in a tiny script of your own** (Node 18+)

In an empty folder, run `npm install @akindats/natlas`, save this as `test.mjs`, and run `node test.mjs`:

```js
import { NAtlas } from "@akindats/natlas";

const natlas = new NAtlas({
  baseUrl: "https://exalted-herbal-bulge.ngrok-free.dev",
  apiKey: "YOUR_KEY",
  clientName: "tester-YOURNAME",
});

console.log(await natlas.ask("Explain inflation simply", { replyIn: "ig" }));
console.log((await natlas.translate("Good morning, how is your family?", "yo")).translation);
for await (const t of natlas.stream("Tell me about Lagos")) process.stdout.write(t);
```

If you see `N-ATLAS 401`, the key is missing or wrong. If you see `Could not reach N-ATLAS server`, check the `baseUrl`.

Prefer the official OpenAI library? It works unchanged: set `baseURL` to `https://exalted-herbal-bulge.ngrok-free.dev/v1` and `apiKey` to your key, and use the model name `n-atlas`.

**4. (Optional) C# / .NET 8:** clone the repo, run `dotnet add reference <path-to>/natlas-devkit/sdk-dotnet/src/NAtlas/NAtlas.csproj` in your console project, then:

```csharp
using var natlas = new NAtlas.NAtlasClient("https://exalted-herbal-bulge.ngrok-free.dev", "YOUR_KEY", "tester-YOURNAME");
Console.WriteLine(await natlas.AskAsync("Explain inflation simply"));
```

**Running your own server instead** (needs ~6 GB free RAM, Python 3.10–3.12): see the Quickstart in the [README](../README.md#quickstart-5-minutes).

## Feedback form (reply by email/WhatsApp)

1. Full name, role, organisation:
2. Your OS and machine (CPU/GPU):
3. Which way did you connect (shared server / your own machine)?
4. Which did you use (browser playground / REST API with curl or PowerShell / TypeScript SDK / .NET SDK)?
5. How many minutes from start to your first N-ATLAS reply?
6. Which languages did you try (English, Hausa, Igbo, Yoruba)?
7. Ease of setup, 1 (hard) to 5 (very easy):
8. What worked well?
9. What broke or confused you?
10. Would you use this in a real project? Why / why not?
11. Do you agree to your name and feedback being included in the NAIC 2026 submission? (yes/no)

Thank you! 🙏
