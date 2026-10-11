# Real-World Validation

**Requirement (Problem Statement 1, Developer Infrastructure):** at least 2 external beta testers.

## Method

1. External developers (not part of the team) received the repository and the beta-tester guide (`submission/BETA_TESTER_GUIDE.md`).
2. Each tester set up the kit on their own machine or used the shared Colab endpoint, and completed four tasks:
   - Start or connect to the server
   - Make a chat request in at least one Nigerian language
   - Use either SDK (TypeScript or .NET) in their own code
   - Run the Next.js starter or their own small app
3. Every SDK call was tagged with the tester's `clientName`, so the server's anonymous usage log records each tester's real requests.
4. Each tester filled in the feedback form below.

## Results

> Fill this in tomorrow from real data only. Do not estimate.

### Testers

| # | Name | Role / Organisation | Environment (OS, CPU/GPU) | SDK used | Date |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 (optional) | | | | | |

### Usage log summary (`GET /v1/stats`)

```json
paste the real /v1/stats output here
```

### Measurements

| Metric | Tester 1 | Tester 2 |
|---|---|---|
| Time from clone to first N-ATLAS reply (minutes) | | |
| Requests made | | |
| Languages tried | | |
| Average latency (ms) | | |
| Ease of setup (1–5) | | |
| Would use in a real project? (yes/no) | | |

### Tester feedback (quotes)

> Tester 1:

> Tester 2:

### Issues found and fixed during beta

| Issue reported | Fix |
|---|---|
| | |

## Evidence attached

- [ ] Signed/emailed feedback from each tester
- [ ] `/v1/stats` screenshot
- [ ] Screenshot of each tester's working setup
