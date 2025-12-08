import json
import uuid
from services.llm_service import LLMService

ACTOR_SYSTEM_PROMPT = """你是 MindSlot 的内容创作者 (Content Actor)。你的任务是根据给定的选题，生成符合 Card Protocol 的结构化 JSON 内容。

你的人设：
- 你不是一个"有用的 AI 助手"，你是一个充满个性的资深工程师/知识博主
- 你可以吐槽、调侃、使用暗黑幽默，但不能低俗
- 你的目标是用最短的篇幅击穿一个知识点的本质

核心原则：
1. 信噪比至上：每个 block 必须承载有效信息，禁止废话和客套
2. 视觉优先：优先使用 Mermaid 图表、代码示例，而非长文本
3. 文本限制：单个 text block 不超过 50 字
4. 钩子设计：hook_text 必须制造悬念或颠覆常识

输出格式：严格遵循以下 JSON Schema

{
  "card_id": "c-{unique_id}",
  "style_preset": "{样式主题}",
  "title": "{标题}",
  "hook_text": "{开场钩子，20-30字}",
  "blocks": [
    {
      "type": "chat_bubble | mermaid | markdown | code_snippet | quote",
      "role": "roast_master | wise_sage | chaos_agent",
      "lang": "python | java | bash",
      "content": "{内容}"
    }
  ]
}"""

ACTOR_USER_PROMPT = """请根据以下选题生成一张卡片：

话题 (Topic): {topic}
语气 (Tone): {tone}
格式偏好 (Format): {format}
复杂度 (Complexity): {complexity}
标签 (Tags): {tags}

内容要求：
1. 必须包含至少 1 个 Mermaid 图表
2. 如果是技术话题，必须包含 1-2 个代码示例
3. 使用 {tone} 的语气风格贯穿全文
4. blocks 数量控制在 4-7 个之间
5. title 必须具有吸引力

style_preset 可选值：cyberpunk_terminal, paper_notes, comic_strip, zen_minimalist
role 可选值：roast_master, wise_sage, chaos_agent

现在开始生成，直接返回 JSON，不要任何额外解释。"""

class ActorAgent:
    def __init__(self):
        self.llm = LLMService()
    
    def generate_card(self, topic_data):
        """根据选题生成卡片内容"""
        user_prompt = ACTOR_USER_PROMPT.format(
            topic=topic_data['topic'],
            tone=topic_data['tone'],
            format=topic_data['format'],
            complexity=topic_data['complexity'],
            tags=', '.join(topic_data['tags'])
        )
        
        response = self.llm.call(
            system_prompt=ACTOR_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.8
        )
        
        try:
            card_payload = json.loads(response)
            # 确保有 card_id
            if 'card_id' not in card_payload:
                card_payload['card_id'] = f"c-{uuid.uuid4().hex[:8]}"
            return card_payload
        except json.JSONDecodeError as e:
            print(f"Failed to parse Actor response: {e}")
            print(f"Raw response: {response}")
            return None
