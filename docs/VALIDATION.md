# Real-World Validation

**Requirement (Problem Statement 1, Developer Infrastructure):** at least 2 external beta testers.

## Method

1. External developers (not part of the team) received the [beta-tester guide](../submission/BETA_TESTER_GUIDE.md), the shared server URL and an API key.
2. Each tester connected to the shared server (N-ATLAS on the team's GPU, exposed over HTTPS) and worked through the guide:
   - Try the browser playground and ask in a Nigerian language
   - Check the server and make a chat request in at least one Nigerian language
   - Use either SDK (TypeScript or .NET) in their own code
   - Optionally run the Next.js starter
3. The server's anonymous usage log records every request (endpoint, client name, detected language, latency; never message text). Testers open the playground as `/?tester=NAME`, and SDK users set `clientName`, so each tester's requests are credited to them.
4. Each tester answered the feedback form in the guide and agreed to their name and feedback being included.

## Results

Filled from real data only.

### Testers

| # | Name | Role / Organisation | Environment | Used | Date |
|---|---|---|---|---|---|
| 1 | Abdul-Raheed Muhammad-Saeed | QA Engineer / Software Developer | Android 10 smartphone (Tecno Camon 40), mobile browser | Browser playground on the shared server | 12 Oct 2026 |
| 2 | Omolaja Ma'mun | Not stated | Not stated | Shared server; ".net" written in the form | 12 Oct 2026 |

### Measurements

| Metric | Tester 1 | Tester 2 |
|---|---|---|
| Time from start to first N-ATLAS reply | 1–2 minutes (reported) | Not stated |
| Requests made (server log) | 5 chat requests, 12:28–12:30 | Not attributed in the log |
| Languages tried | Yoruba, Hausa (and English) | Not stated |
| Average latency (server log) | 3.3 s per streamed reply | "Very fast, faster than I expected" (reported) |
| Ease of setup | 4 out of 5 | "Easy" |
| Would use in a real project? | Yes, potentially | "Yes of course, it's very responsive, I love that" |

### Tester feedback (quotes)

> **Tester 1:** "The interface was simple to use on my Android phone. N-ATLAS successfully detected Yoruba and Hausa messages. It also responded appropriately to the Yoruba greeting 'Bawo ni' with 'Hello! How can I assist you today?'"
>
> On using it in a real project: "Yes, potentially. The interface is easy to access, and automatic language detection could be useful for multilingual applications. However, I would want more consistent Yoruba and Hausa understanding, better handling of spelling variations, and additional testing before using it in production."

> **Tester 2:** What worked well: "It's very fast, [faster] than I expected." Would use it in a real project: "Yes of course, it's very responsive, I love that." What broke or confused: "Each chat shows language detected, but it can't reply in the language given to it."

### Issues found and fixed during beta

| Issue reported | Status | Fix |
|---|---|---|
| With **Reply in: English**, Hausa "Yaya kake" got "please communicate in English" (Tester 1) | **Fixed** the same day | The reply-language prompt now tells the model it understands all four languages and names the detected input language: "(This message is in Hausa. Reply in English.)". Re-tested through the public URL: "Yaya kake" now gets "I'm doing well, thanks for asking. How are you?" |
| "Bawoni" (one word) with English forced got the same refusal, while "Bawo ni" worked (Tester 1) | **Known limitation** | A model-level weakness with short or misspelled Yoruba and Igbo when asked to answer in another language. Documented in the README; **Auto** (reply in the user's language) avoids it, and the tester guide now recommends Auto. |
| Replies did not always come back in the chosen reply language (Tester 2) | Same issue as above | Covered by the reply-language fix; the remaining cases are the documented limitation for short or misspelled phrases. |
| Wanted clearer feedback when a language is detected but cannot be processed (Tester 1) | Noted for the roadmap | |
| Found by the team while preparing the beta: a stopped answer kept the model busy for over 120 s behind the proxy | **Fixed** | The Stop button now cancels the answer on the server (`/v1/chat/cancel/{id}`); the next request was answered in 1.1 s. |

### Usage log

The server log covers 12 October 2026 and also contains the team's own testing (client names such as `playground`, `sdk-test` and `dev-…`). Tester 1's session is the five playground requests at 12:28–12:30 with Reply in: English (Yoruba ×2, English ×2, Hausa ×1). From the tester-link change onwards, testers' requests appear as `tester-NAME`.

## Evidence attached

- [x] Tester 1's written feedback (in this document, consent given)
- [x] Tester 2's written feedback (in this document, consent given)
