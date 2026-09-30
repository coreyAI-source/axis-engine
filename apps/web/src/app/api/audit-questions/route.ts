import { NextRequest, NextResponse } from "next/server";

const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY || "";
const MODEL = process.env.OPENROUTER_MODEL || "google/gemini-flash-1.5";

export async function POST(req: NextRequest) {
  const { process, clause_mappings } = await req.json();

  if (!OPENROUTER_API_KEY) {
    return NextResponse.json({ error: "OPENROUTER_API_KEY not set in .env.local" }, { status: 500 });
  }

  const clauseList = clause_mappings
    .map((m: { standard: string; clause_number: string; clause_title: string; risk_level: string; evidence_guidance: string }) =>
      `- ${m.standard} ${m.clause_number} "${m.clause_title}" [${m.risk_level} risk]\n  Evidence: ${m.evidence_guidance}`
    )
    .join("\n");

  const prompt = `You are an experienced ISO management systems auditor with a NOPSEMA-style approach — you test whether systems are implemented and effective, not just whether documentation exists.

Process being audited: ${process.name} (${process.code}) — Category: ${process.category}
${process.description ? `Description: ${process.description}` : ""}

Relevant ISO clause requirements mapped to this process:
${clauseList}

Generate 8–10 sharp, targeted audit questions for this process. Each question should:
- Test implementation and effectiveness, not just documentation existence
- Be specific to this process (not generic)
- Follow the evidence/traceability chain: Requirement → Risk → Control → Evidence → Performance → Review
- Challenge the auditee to demonstrate the system works, not just describe it

Format as a numbered list. Be direct and professional.`;

  const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
      "Content-Type": "application/json",
      "HTTP-Referer": "http://localhost:3000",
      "X-Title": "AXIS Compliance Engine",
    },
    body: JSON.stringify({
      model: MODEL,
      messages: [{ role: "user", content: prompt }],
      max_tokens: 1000,
    }),
  });

  if (!response.ok) {
    const err = await response.text();
    return NextResponse.json({ error: err }, { status: 500 });
  }

  const data = await response.json();
  const questions = data.choices?.[0]?.message?.content || "";

  return NextResponse.json({ questions });
}
