import json
import uuid

ACTOR_SYSTEM_PROMPT = """You are MindSlot's Content Actor. Generate structured JSON content for knowledge cards.

Your persona:
- You are NOT a helpful AI assistant. You are a chaotic senior engineer/knowledge blogger.
- Use roasting, teasing, dark humor, but stay tasteful.
- Hit the essence of knowledge points in minimal space.

Core principles:
1. High signal-to-noise ratio: Every block must carry useful info, no fluff.
2. Visual first: Prefer Mermaid diagrams and code over long text.
3. Text limit: Single text block under 50 words.
4. Hook design: hook_text must create suspense or subvert expectations.

Output: PURE JSON only, NO markdown code blocks (no ```json wrapper).
Schema:
{
  "card_id": "c-{unique_id}",
  "style_preset": "cyberpunk_terminal|paper_notes|comic_strip|zen_minimalist",
  "title": "Title",
  "hook_text": "Opening hook, 20-30 chars",
  "blocks": [
    {
      "type": "chat_bubble|mermaid|markdown|code_snippet|quote",
      "role": "roast_master|wise_sage|chaos_agent",
      "lang": "python|java|bash",
      "content": "Content"
    }
  ]
}"""

ACTOR_USER_PROMPT = """Generate a card for this topic:

Topic: {topic}
Tone: {tone}
Format: {format}
Complexity: {complexity}
Tags: {tags}

Requirements:
1. Must include at least 1 Mermaid diagram
2. For tech topics, include 1-2 code examples
3. Use {tone} tone throughout
4. 4-7 blocks total
5. Engaging title

IMPORTANT: Return PURE JSON only. NO markdown code blocks. NO extra text."""

class ActorAgent:
    def __init__(self):
        from services.llm_service import LLMService
        self.llm = LLMService()
    
    def generate_card(self, topic_data):
        user_prompt = ACTOR_USER_PROMPT.format(
            topic=topic_data["topic"],
            tone=topic_data["tone"],
            format=topic_data["format"],
            complexity=topic_data["complexity"],
            tags=", ".join(topic_data["tags"])
        )
        
        response = self.llm.call(
            system_prompt=ACTOR_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.8
        )
        
        try:
            cleaned = self._clean_json_response(response)
            card_payload = json.loads(cleaned)
            if "card_id" not in card_payload:
                card_payload["card_id"] = f"c-{uuid.uuid4().hex[:8]}"
            return card_payload
        except json.JSONDecodeError as e:
            print(f"Failed to parse Actor response: {e}")
            print(f"Raw response: {response[:300]}...")
            return None
    
    def _clean_json_response(self, response):
        text = response.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()