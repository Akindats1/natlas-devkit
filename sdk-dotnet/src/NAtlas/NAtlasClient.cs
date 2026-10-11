// NAtlas — .NET SDK for N-ATLAS, Nigeria's multilingual LLM.
// N-ATLaS is an initiative of the Federal Ministry of Communications,
// Innovation and Digital Economy, and powered by Awarri Technologies.

using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
using System.Runtime.CompilerServices;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading;
using System.Threading.Tasks;

namespace NAtlas
{
    /// <summary>Languages supported by N-ATLAS.</summary>
    public enum Language { English, Hausa, Igbo, Yoruba }

    public static class Languages
    {
        public static string Code(Language l)
        {
            switch (l)
            {
                case Language.Hausa: return "ha";
                case Language.Igbo: return "ig";
                case Language.Yoruba: return "yo";
                default: return "en";
            }
        }

        public static Language FromCode(string code)
        {
            switch ((code ?? "").ToLowerInvariant())
            {
                case "ha": return Language.Hausa;
                case "ig": return Language.Igbo;
                case "yo": return Language.Yoruba;
                default: return Language.English;
            }
        }

        public const string Attribution =
            "N-ATLaS is an initiative of the Federal Ministry of Communications, Innovation and Digital Economy, and powered by Awarri Technologies.";
    }

    public sealed class ChatMessage
    {
        [JsonPropertyName("role")] public string Role { get; set; } = "user";
        [JsonPropertyName("content")] public string Content { get; set; } = "";

        public ChatMessage() { }
        public ChatMessage(string role, string content) { Role = role; Content = content; }

        public static ChatMessage System(string c) => new ChatMessage("system", c);
        public static ChatMessage User(string c) => new ChatMessage("user", c);
        public static ChatMessage Assistant(string c) => new ChatMessage("assistant", c);
    }

    public sealed class ChatOptions
    {
        public int MaxTokens { get; set; } = 512;
        public double Temperature { get; set; } = 0.1;
        public double TopP { get; set; } = 0.95;
        /// <summary>Force the reply language, whatever language the user wrote in.</summary>
        public Language? ReplyIn { get; set; }
    }

    public sealed class Usage
    {
        [JsonPropertyName("prompt_tokens")] public int PromptTokens { get; set; }
        [JsonPropertyName("completion_tokens")] public int CompletionTokens { get; set; }
        [JsonPropertyName("total_tokens")] public int TotalTokens { get; set; }
    }

    public sealed class ChatResult
    {
        public string Text { get; set; } = "";
        public Usage Usage { get; set; } = new Usage();
    }

    public sealed class TranslateResult
    {
        [JsonPropertyName("translation")] public string Translation { get; set; } = "";
        [JsonPropertyName("source")] public string? Source { get; set; }
        [JsonPropertyName("target")] public string Target { get; set; } = "";
        [JsonPropertyName("usage")] public Usage Usage { get; set; } = new Usage();
    }

    public sealed class DetectResult
    {
        [JsonPropertyName("language")] public string Code { get; set; } = "en";
        [JsonPropertyName("name")] public string Name { get; set; } = "English";
        [JsonPropertyName("confidence")] public double Confidence { get; set; }
        [JsonIgnore] public Language Language => Languages.FromCode(Code);
    }

    public sealed class NAtlasException : Exception
    {
        public int? StatusCode { get; }
        public NAtlasException(string message, int? status = null, Exception? inner = null)
            : base(message, inner) { StatusCode = status; }
    }

    /// <summary>
    /// Client for an N-ATLAS OpenAI-compatible server (see /server in the dev kit).
    /// Thread-safe; create one and reuse it.
    /// </summary>
    public sealed class NAtlasClient : IDisposable
    {
        private readonly HttpClient _http;
        private readonly bool _ownsHttp;
        private static readonly JsonSerializerOptions Json = new JsonSerializerOptions
        {
            DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
        };

        public Uri BaseUrl { get; }

        /// <param name="baseUrl">e.g. http://localhost:8000 (defaults to NATLAS_BASE_URL env var)</param>
        /// <param name="apiKey">Optional bearer key (defaults to NATLAS_API_KEY env var)</param>
        /// <param name="clientName">Sent as X-Client-Name for the server's usage log</param>
        /// <param name="httpClient">Optional HttpClient to reuse (e.g. from IHttpClientFactory)</param>
        /// <param name="timeout">Request timeout (default 2 minutes; 8B models on CPU can be slow)</param>
        public NAtlasClient(string? baseUrl = null, string? apiKey = null, string? clientName = null,
                            HttpClient? httpClient = null, TimeSpan? timeout = null)
        {
            var url = baseUrl ?? Environment.GetEnvironmentVariable("NATLAS_BASE_URL") ?? "http://localhost:8000";
            url = url.TrimEnd('/');
            if (url.EndsWith("/v1")) url = url.Substring(0, url.Length - 3);
            BaseUrl = new Uri(url + "/");

            _ownsHttp = httpClient == null;
            _http = httpClient ?? new HttpClient();
            _http.Timeout = timeout ?? TimeSpan.FromMinutes(2);

            var key = apiKey ?? Environment.GetEnvironmentVariable("NATLAS_API_KEY");
            if (!string.IsNullOrEmpty(key))
                _http.DefaultRequestHeaders.Authorization =
                    new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", key);
            if (!string.IsNullOrEmpty(clientName))
                _http.DefaultRequestHeaders.Add("X-Client-Name", clientName);
        }

        // ---------- public API ----------

        /// <summary>One prompt in, text out.</summary>
        public async Task<string> AskAsync(string prompt, ChatOptions? options = null, CancellationToken ct = default)
            => (await ChatAsync(new[] { ChatMessage.User(prompt) }, options, ct).ConfigureAwait(false)).Text;

        public async Task<ChatResult> ChatAsync(IEnumerable<ChatMessage> messages, ChatOptions? options = null,
                                                CancellationToken ct = default)
        {
            using (var res = await SendAsync("v1/chat/completions", Body(messages, options, false),
                                             HttpCompletionOption.ResponseContentRead, ct).ConfigureAwait(false))
            {
                var json = await res.Content.ReadAsStringAsync().ConfigureAwait(false);
                using (var doc = JsonDocument.Parse(json))
                {
                    var root = doc.RootElement;
                    var text = root.GetProperty("choices")[0].GetProperty("message").GetProperty("content").GetString() ?? "";
                    var usage = root.TryGetProperty("usage", out var u)
                        ? JsonSerializer.Deserialize<Usage>(u.GetRawText()) ?? new Usage()
                        : new Usage();
                    return new ChatResult { Text = text, Usage = usage };
                }
            }
        }

        /// <summary>Stream tokens as they are generated: <c>await foreach (var t in client.StreamAsync(...))</c></summary>
        public async IAsyncEnumerable<string> StreamAsync(IEnumerable<ChatMessage> messages, ChatOptions? options = null,
                                                          [EnumeratorCancellation] CancellationToken ct = default)
        {
            using (var res = await SendAsync("v1/chat/completions", Body(messages, options, true),
                                             HttpCompletionOption.ResponseHeadersRead, ct).ConfigureAwait(false))
            using (var stream = await res.Content.ReadAsStreamAsync().ConfigureAwait(false))
            using (var reader = new StreamReader(stream, Encoding.UTF8))
            {
                string? line;
                while ((line = await reader.ReadLineAsync().ConfigureAwait(false)) != null)
                {
                    ct.ThrowIfCancellationRequested();
                    if (!line.StartsWith("data:")) continue;
                    var data = line.Substring(5).Trim();
                    if (data == "[DONE]") yield break;
                    using (var doc = JsonDocument.Parse(data))
                    {
                        var delta = doc.RootElement.GetProperty("choices")[0].GetProperty("delta");
                        if (delta.TryGetProperty("content", out var c))
                        {
                            var piece = c.GetString();
                            if (!string.IsNullOrEmpty(piece)) yield return piece!;
                        }
                    }
                }
            }
        }

        public IAsyncEnumerable<string> StreamAsync(string prompt, ChatOptions? options = null, CancellationToken ct = default)
            => StreamAsync(new[] { ChatMessage.User(prompt) }, options, ct);

        /// <summary>Translate between English, Hausa, Igbo and Yoruba.</summary>
        public async Task<TranslateResult> TranslateAsync(string text, Language target, Language? source = null,
                                                          CancellationToken ct = default)
        {
            var body = JsonSerializer.Serialize(new Dictionary<string, object?>
            {
                ["text"] = text,
                ["target"] = Languages.Code(target),
                ["source"] = source.HasValue ? Languages.Code(source.Value) : null,
            }, Json);
            return await PostJson<TranslateResult>("v1/translate", body, ct).ConfigureAwait(false);
        }

        public Task<DetectResult> DetectLanguageAsync(string text, CancellationToken ct = default)
            => PostJson<DetectResult>("v1/detect-language",
                                      JsonSerializer.Serialize(new Dictionary<string, string> { ["text"] = text }), ct);

        public async Task<bool> IsHealthyAsync(CancellationToken ct = default)
        {
            try
            {
                using (var res = await _http.GetAsync(new Uri(BaseUrl, "health"), ct).ConfigureAwait(false))
                    return res.IsSuccessStatusCode;
            }
            catch { return false; }
        }

        public void Dispose() { if (_ownsHttp) _http.Dispose(); }

        // ---------- internals ----------

        private static string Body(IEnumerable<ChatMessage> messages, ChatOptions? o, bool stream)
        {
            o = o ?? new ChatOptions();
            return JsonSerializer.Serialize(new Dictionary<string, object?>
            {
                ["model"] = "n-atlas",
                ["messages"] = messages,
                ["stream"] = stream,
                ["max_tokens"] = o.MaxTokens,
                ["temperature"] = o.Temperature,
                ["top_p"] = o.TopP,
                ["reply_language"] = o.ReplyIn.HasValue ? Languages.Code(o.ReplyIn.Value) : null,
            }, Json);
        }

        private async Task<T> PostJson<T>(string path, string body, CancellationToken ct)
        {
            using (var res = await SendAsync(path, body, HttpCompletionOption.ResponseContentRead, ct).ConfigureAwait(false))
            {
                var json = await res.Content.ReadAsStringAsync().ConfigureAwait(false);
                return JsonSerializer.Deserialize<T>(json, Json)
                       ?? throw new NAtlasException("Empty response from N-ATLAS server");
            }
        }

        private async Task<HttpResponseMessage> SendAsync(string path, string body, HttpCompletionOption mode,
                                                          CancellationToken ct)
        {
            var req = new HttpRequestMessage(HttpMethod.Post, new Uri(BaseUrl, path))
            {
                Content = new StringContent(body, Encoding.UTF8, "application/json"),
            };
            HttpResponseMessage res;
            try
            {
                res = await _http.SendAsync(req, mode, ct).ConfigureAwait(false);
            }
            catch (HttpRequestException e)
            {
                throw new NAtlasException($"Could not reach N-ATLAS server at {BaseUrl}. Is it running? ({e.Message})", null, e);
            }
            if (!res.IsSuccessStatusCode)
            {
                var text = await res.Content.ReadAsStringAsync().ConfigureAwait(false);
                var code = (int)res.StatusCode;
                res.Dispose();
                throw new NAtlasException($"N-ATLAS {code}: {text}", code);
            }
            return res;
        }
    }
}
