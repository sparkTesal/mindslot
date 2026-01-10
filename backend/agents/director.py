import json

DIRECTOR_SYSTEM_PROMPT = """You are MindSlot's Content Director. Generate high-quality topic lists for an immersive learning app.

Your responsibilities:
1. Generate diverse topics covering tech, history, science, culture
2. Assign appropriate tone and format to each topic
3. Ensure content is both deep and entertaining

Output format: Pure JSON array only, NO markdown code blocks (no ```json).
Each object must contain:
- topic: Topic title (string, in Chinese)
- tone: Style (Excited/Sarcastic/Philosophical/Playful/Dark_Humor)
- format: Presentation (code_comparison/rant/story/debate/meme_analysis)
- complexity: 1-5 (1=general, 5=hardcore)
- tags: Array of tags"""

DIRECTOR_USER_PROMPT = """Generate {count} card topics for domains: {domains}

Requirements:
1. Topics must be specific and controversial or counter-intuitive
2. 60% tech, 30% general knowledge, 10% memes/fun
3. Diverse tones
4. Each topic consumable in 2-3 minutes

IMPORTANT: Return PURE JSON array only. NO ```json wrapper. NO extra text. Start with [ end with ]"""

class DirectorAgent:
    def __init__(self):
        from services.llm_service import LLMService
        self.llm = LLMService()
    
    def generate_topics(self, count=20, domains="Java, Python, AI, History, Science"):
        """生成选题清单"""
        user_prompt = DIRECTOR_USER_PROMPT.format(count=count, domains=domains)
        
        response = self.llm.call(
            system_prompt=DIRECTOR_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.9
        )
        
        try:
            # 清理 Markdown 代码块标记
            cleaned = self._clean_json_response(response)
            topics = json.loads(cleaned)
            return topics
        except json.JSONDecodeError as e:
            print(f"Failed to parse Director response: {e}")
            print(f"Raw response: {response[:300]}...")
            return []
    
    def _clean_json_response(self, response: str) -> str:
        """清理 LLM 返回的 JSON，去掉 Markdown 代码块标记"""
        text = response.strip()
        # 去掉 ```json 或 ``` 开头
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        # 去掉结尾的 ```
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()