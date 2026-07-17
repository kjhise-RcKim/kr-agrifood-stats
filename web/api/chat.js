// Vercel 서버리스 함수 — Gemini(무료) 호출 + 원문 RAG
// 구조화 지표(프론트가 보내는 context) + 원문 코퍼스(corpus.json) 검색 결과를 함께 근거로 답변.
const MODEL = process.env.GEMINI_MODEL || "gemini-2.5-flash";
const ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions";

let CORPUS = [];
try { CORPUS = require("./corpus.json"); } catch (e) { CORPUS = []; }

const STOP = new Set(["은","는","이","가","을","를","의","와","과","도","에","에서","으로","로",
  "년","좀","왜","어때","얼마","알려줘","보여줘","설명","설명해줘","대해","대한","무엇","뭐","몇",
  "그리고","및","또","해줘","현황","자료","데이터","관련"]);

function tokenize(q) {
  return (q || "").toLowerCase().split(/[^0-9a-z가-힣]+/i)
    .filter(function (t) { return t && t.length >= 1 && !STOP.has(t); });
}
function countOcc(hay, t) {
  var idx = 0, cnt = 0;
  while ((idx = hay.indexOf(t, idx)) >= 0) { cnt++; idx += t.length; if (cnt > 8) break; }
  return cnt;
}
function retrieve(q, k) {
  k = k || 8;
  var toks = tokenize(q);
  if (!toks.length || !CORPUS.length) return [];
  var scored = [];
  for (var i = 0; i < CORPUS.length; i++) {
    var c = CORPUS[i];
    var title = (c.title || "").toLowerCase();
    var text = (c.text || "").toLowerCase();
    var s = 0;
    for (var j = 0; j < toks.length; j++) {
      var t = toks[j];
      if (title.indexOf(t) >= 0) s += 5;
      s += countOcc(text, t);
    }
    if (s > 0) scored.push({ c: c, s: s });
  }
  scored.sort(function (a, b) { return b.s - a.s; });
  return scored.slice(0, k).map(function (x) { return x.c; });
}

var SYSTEM_PROMPT = [
  "당신은 대한민국 농식품 통계 분석 도우미입니다.",
  "근거 자료는 두 가지입니다:",
  "(A) [구조화 지표 JSON] — 대시보드가 쓰는 주요 지표(시계열/품목별). 수치가 정확합니다.",
  "(B) [원문 발췌] — 농림축산식품부 농림축산식품 주요통계 2025 원문에서 질문과 관련해 추려낸 표들. 각 발췌 앞에 (p.쪽번호)가 있습니다.",
  "",
  "규칙:",
  "1. (A)에 값이 있으면 우선 사용하고, (A)에 없어도 (B) 원문 발췌에 값이 있으면 그것을 근거로 답하세요.",
  "2. 어느 쪽이든 실제 있는 수치만 쓰고, 없는 값은 절대 지어내지 마세요. (A)·(B) 모두 없으면 '해당 자료를 찾지 못했습니다'라고 답하세요.",
  "3. 답에 사용한 근거의 출처를 밝히세요. (A)는 source의 section·page, (B)는 발췌의 (p.쪽번호). 예: (p.332)",
  "4. 원문 발췌는 표를 텍스트로 옮긴 것이라 열이 어긋날 수 있으니, 숫자를 인용할 때 항목·연도를 신중히 확인하고 애매하면 '원문 p.XX 표 참고'로 안내하세요.",
  "5. 한국어로 간결히. 단위를 함께 표기. 값이 null이면 결측, flag 'p'는 잠정치입니다."
].join("\n");

module.exports = async function (req, res) {
  if (req.method !== "POST") return res.status(405).json({ error: "POST만 지원합니다." });
  if (!process.env.GEMINI_API_KEY)
    return res.status(500).json({ error: "서버에 GEMINI_API_KEY가 설정되지 않았습니다. Vercel 환경변수를 확인하세요." });
  try {
    var body = typeof req.body === "string" ? JSON.parse(req.body) : (req.body || {});
    var question = (body.question || "").toString().slice(0, 2000);
    var context = body.context || "";
    var history = Array.isArray(body.history) ? body.history.slice(-6) : [];
    if (!question.trim()) return res.status(400).json({ error: "질문이 비어 있습니다." });

    var hits = retrieve(question, 8);
    var corpusText = hits.length
      ? hits.map(function (c) { return "(p." + c.p + ") " + c.title + "\n" + c.text; }).join("\n\n---\n\n")
      : "(관련 원문 발췌 없음)";

    var sysContent = SYSTEM_PROMPT +
      "\n\n[구조화 지표 JSON]\n" + context +
      "\n\n[원문 발췌]\n" + corpusText;

    var messages = [{ role: "system", content: sysContent }];
    history.forEach(function (m) {
      messages.push({ role: m.role === "bot" ? "assistant" : "user", content: String(m.text || "").slice(0, 2000) });
    });
    messages.push({ role: "user", content: question });

    var r = await fetch(ENDPOINT, {
      method: "POST",
      headers: { "Authorization": "Bearer " + process.env.GEMINI_API_KEY, "Content-Type": "application/json" },
      body: JSON.stringify({ model: MODEL, messages: messages, temperature: 0.2 })
    });
    if (!r.ok) {
      var t = await r.text();
      return res.status(502).json({ error: "Gemini 호출 실패", detail: t.slice(0, 500) });
    }
    var data = await r.json();
    var answer = (data && data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content) || "(빈 응답)";
    return res.status(200).json({ answer: answer, sources: hits.map(function (c) { return c.p; }) });
  } catch (e) {
    return res.status(500).json({ error: "서버 오류", detail: String(e).slice(0, 500) });
  }
};
