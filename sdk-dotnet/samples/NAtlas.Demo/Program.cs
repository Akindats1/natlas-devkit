using NAtlas;

using var natlas = new NAtlasClient(clientName: "dotnet-demo");

if (!await natlas.IsHealthyAsync())
{
    Console.WriteLine($"N-ATLAS server not reachable at {natlas.BaseUrl}. Start it first (see /server).");
    return 1;
}

// 1. Simple question
Console.WriteLine(await natlas.AskAsync("What is a construction site daily report?"));

// 2. Force the reply into Hausa
Console.WriteLine(await natlas.AskAsync("Explain safety helmets to site workers",
    new ChatOptions { ReplyIn = Language.Hausa }));

// 3. Translate
var t = await natlas.TranslateAsync("Concrete pouring starts at 7am tomorrow", Language.Yoruba);
Console.WriteLine(t.Translation);

// 4. Detect language
var d = await natlas.DetectLanguageAsync("Kedu ka ị mere?");
Console.WriteLine($"Detected: {d.Name} ({d.Confidence:P0})");

// 5. Stream token by token
await foreach (var token in natlas.StreamAsync("Give 3 tips for Lagos commuters"))
    Console.Write(token);
Console.WriteLine();

Console.WriteLine(Languages.Attribution);
return 0;
