# N-ATLAS Dev Kit — Beta Tester Guide (15–20 minutes)

Thank you for testing! N-ATLAS is Nigeria's own AI model (English, Hausa, Igbo, Yoruba). This kit lets developers use it like the OpenAI API.

## Pick ONE way to connect

**Easy (no setup):** use the shared server Akindats sends you.

```
NATLAS_BASE_URL = <URL from Akindats>
NATLAS_API_KEY  = <key from Akindats>
```

**Full (your own machine, needs ~6 GB free RAM):**

```bash
git clone <repo URL>
cd natlas-devkit/server
pip install -r requirements.txt
python -m natlas_server
```

## Tasks

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

TypeScript:

```ts
import { NAtlas } from "natlas";
const natlas = new NAtlas({ clientName: "tester-YOURNAME" }); // reads NATLAS_BASE_URL / NATLAS_API_KEY
console.log(await natlas.ask("YOUR QUESTION", { replyIn: "ig" }));
```

or C#:

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
