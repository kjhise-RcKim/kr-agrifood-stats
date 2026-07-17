// Vercel 서버리스 함수 — Gemini(무료 티어) 호출로 데이터 근거 답변
// 환경변수 GEMINI_API_KEY 필요 (Vercel > Settings > Environment Variables)
// OpenAI 호환 엔드포인트 사용. 키는 서버에만 있고 프론트에 노출되지 않음.

const MODEL = process.env.GEMINI_MODEL || "gemini-2.5-flash";
const ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions";

const SYSTEM_PROMPT = `당신은 대한민국 농식품 통계 분석 도우미입니다.
아래 제공되는 JSON 데이터(농림축산식품부 『농림축산식품 주요통계 2025』)에 있는 수치만 근거로 답합니다.

반드시 지킬 규칙:
1. 데이터에 없는 수치는 절대 지어내지 마세요. 관련 값이 없으면 "해당 데이터가 자료에 없습니다"라고 답하세요.
2. 답에 사용한 지표는 출처(source의 section과 page)를 괄호로 함께 밝히세요. 예: (기본통계 Ⅶ 농가경제, p.152)
3. 한국어로 간결하고 명확하게 답하세요. 표나 짧은 목록을 적절히 사용하세요.
4. 추세·비교·해석을 제시할 때는 반드시 실제 수치를 인용하고, 계산(증감률 등)은 제공된 값으로만 수행하세요.
5. 추정이나 의견은 "추정"임을 밝히고 근거 수치를 함께 제시하세요.
6. series의 value가 null인 해는 결측입니다. flag가 "p"인 값은 잠정치입니다.
7. 단위(unit)를 반드시 함께 표기하세요.`;

module.exports = async (req, res) => {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "POST만 지원합니다." });
  }
  if (!process.env.GEMINI_API_KEY) {
    return res.status(500).json({ error: "서버에 GEMINI_API_KEY가 설정되지 않았습니다. Vercel 환경변수를 확인하세요." });
  }
  try {
    const body = typeof req.body === "string" ? JSON.parse(req.body) : (req.body || {});
    const question = (body.question || "").toString().slice(0, 2000);
    const context = body.context || "";
    const history = Array.isArray(body.history) ? body.history.slice(-6) : [];
    if (!question.trim()) {
      return res.status(400).json({ error: "질문이 비어 있습니다." });
    }

    const messages = [
      { role: "system", content: SYSTEM_PROMPT + "\n\n[데이터 JSON]\n" + context },
      ...history.map(m => ({ role: m.role === "bot" ? "assistant" : "user", content: String(m.text || "").slice(0, 2000) })),
      { role: "user", content: question },
    ];

    const r = await fetch(ENDPOINT, {
      method: "POST",
      headers: {
        "Authorization": "Bearer " + process.env.GEMINI_API_KEY,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ model: MODEL, messages, temperature: 0.2 }),
    });

    if (!r.ok) {
      const t = await r.text();
      return res.status(502).json({ error: "Gemini 호출 실패", detail: t.slice(0, 500) });
    }
    const data = await r.json();
    const answer = data?.choices?.[0]?.message?.content || "(빈 응답)";
    return res.status(200).json({ answer });
  } catch (e) {
    return res.status(500).json({ error: "서버 오류", detail: String(e).slice(0, 500) });
  }
};
