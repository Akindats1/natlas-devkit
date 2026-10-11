# Submission Checklist — Monday 12 October 2026

**Hard deadline: 11:59 PM WAT. Aim to submit by 9:00 PM.**

## Tonight (before you sleep)
- [ ] Log in to Hugging Face and accept the terms at https://huggingface.co/NCAIR1/N-ATLaS
- [ ] Start the 4.9 GB model download so it finishes overnight:
      `cd server && pip install -r requirements.txt && python -m natlas_server`
- [ ] Message 3–4 developer friends now asking them to test tomorrow morning (you need at least 2; ask more in case some don't reply). Send them `submission/BETA_TESTER_GUIDE.md`.
- [ ] Confirm a teammate (the track card says teams of 2–5). Email naic@nitda.gov.ng if applying solo.

## Morning (by 12 PM)
- [ ] Check the real model answers: `curl localhost:8000/health` should show `"backend": "llamacpp"`
- [ ] Push the repo to GitHub (public)
- [ ] Run the Colab notebook (or expose your laptop with ngrok) so testers have a shared URL; set `NATLAS_API_KEY`
- [ ] Send testers the URL + key
- [ ] Try a few real prompts in Hausa/Igbo/English; note anything odd for the "Known limitations" section

## Afternoon (by 5 PM)
- [ ] Collect tester feedback forms
- [ ] Save `/v1/stats` output and screenshot it
- [ ] Fill in `docs/VALIDATION.md` with REAL numbers only
- [ ] Take screenshots: health check, Hausa answer, starter app, .NET demo, `/docs` page
- [ ] (Optional) publish SDK to npm: `cd sdk-typescript && npm publish`

## Evening (by 8 PM)
- [ ] Record the 3–5 minute video using `submission/VIDEO_SCRIPT.md`; upload to YouTube (unlisted) or Google Drive (anyone with link)
- [ ] Finalise `submission/APPLICATION_ANSWERS.md`

## Submit (by 9 PM)
Fill the form at https://ondi.innox.africa/apply/naic/naic-innovation-enterprise with the 7 items:
1. [ ] Working artefact → GitHub repo link (+ live URL if available)
2. [ ] N-ATLAS integration evidence → `docs/NATLAS_INTEGRATION.md` link + screenshots
3. [ ] Real-world validation → `docs/VALIDATION.md` + tester feedback
4. [ ] Technical documentation → README + `docs/ARCHITECTURE.md`
5. [ ] Video demonstration → link
6. [ ] Team profile → names, roles, affiliations
7. [ ] CAC certificate (Peachel Innovations Limited) or valid ID

- [ ] Screenshot the confirmation page / save the confirmation email
