# NAtlas (.NET)

.NET SDK for **N-ATLAS**, Nigeria's multilingual LLM. Targets `net8.0` and `netstandard2.0` (works in .NET Framework 4.6.1+ apps, including Revit and AutoCAD plugins).

```csharp
using NAtlas;
using var natlas = new NAtlasClient("http://localhost:8000"); // or NATLAS_BASE_URL env

string a = await natlas.AskAsync("Explain inflation simply", new ChatOptions { ReplyIn = Language.Hausa });
var r = await natlas.ChatAsync(new[] { ChatMessage.System("Be brief."), ChatMessage.User("Kedu?") });
await foreach (var t in natlas.StreamAsync("Tell me about Lagos")) Console.Write(t);
var tr = await natlas.TranslateAsync("Site meeting at 9am", Language.Igbo);
var d = await natlas.DetectLanguageAsync("Sannu, yaya kake?");
```

Run the demo: `dotnet run --project samples/NAtlas.Demo` (needs a running N-ATLAS server).

> N-ATLaS is an initiative of the Federal Ministry of Communications, Innovation and Digital Economy, and powered by Awarri Technologies.
