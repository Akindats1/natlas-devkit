import { NAtlasError, type Language } from "@akindats/natlas";
import { natlas } from "../../lib";

export async function POST(req: Request) {
  const { text, target, source } = (await req.json()) as { text: string; target: Language; source?: Language };
  try {
    return Response.json(await natlas.translate(text, target, source));
  } catch (e) {
    const status = e instanceof NAtlasError ? e.status ?? 502 : 500;
    return Response.json({ error: (e as Error).message }, { status });
  }
}
