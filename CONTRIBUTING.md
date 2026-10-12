# Contributing to the N-ATLAS Dev Kit

Thank you for helping Nigerian developers build with N-ATLAS. Bug reports, fixes, new examples, documentation and translations are all welcome.

## Ways to contribute

- **Report a bug or a wrong answer.** Open an issue with what you ran, what you expected and what happened. For model output, include the language and the prompt (no personal data).
- **Fix or improve something.** Open an issue first for anything larger than a small fix, so we can agree on the approach.
- **Improve the docs.** Clearer setup steps, more examples, or guides in Hausa, Igbo or Yoruba.

## Set up

```bash
git clone https://github.com/Akindats1/natlas-devkit.git
cd natlas-devkit/server
pip install fastapi uvicorn httpx pytest
NATLAS_BACKEND=mock python -m natlas_server   # no model download needed
```

Mock mode serves the full API without the model, which is enough for most changes. To run the real model, follow the Quickstart in the [README](README.md).

## Run the tests

Run the tests for the part you changed before opening a pull request:

```bash
# server (from server/)
pytest

# TypeScript SDK (needs a running server; mock mode is fine)
cd sdk-typescript && npm install && npm run build && npm test

# .NET SDK
cd sdk-dotnet && dotnet run --project samples/NAtlas.Demo
```

Add a test for every bug you fix and every feature you add.

## Pull requests

1. Fork the repository and create a branch from `main`.
2. Keep each pull request to one change. Match the style of the surrounding code.
3. Update the README or docs when you change behaviour.
4. Describe what you changed, why, and how you tested it.

## Ground rules

- **Never commit secrets:** API keys, Hugging Face tokens, `.env` files or model weights. They are ignored by `.gitignore`; keep it that way.
- **Keep the attribution.** The `X-Powered-By` header and the `ATTRIBUTION` text are required by the N-ATLaS Terms of Use.
- **Respect the N-ATLaS Terms of Use.** Contributions must not enable the prohibited uses listed in the [README](README.md#licence) (surveillance, discriminatory profiling, disinformation, military use, or harmful applications).
- **Be kind.** Treat everyone with respect; harassment of any kind is not tolerated.

## Licence

By contributing, you agree that your contributions are licensed under the [MIT License](LICENSE). The N-ATLAS model itself stays under the N-ATLaS Terms of Use (Awarri Technologies / FMCIDE).
