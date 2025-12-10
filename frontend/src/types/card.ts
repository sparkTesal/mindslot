export interface CardPayload {
  card_id: string;
  style_preset: 'cyberpunk_terminal' | 'paper_notes' | 'comic_strip' | 'zen_minimalist';
  title: string;
  hook_text: string;
  blocks: Block[];
}

export type BlockType = 'chat_bubble' | 'mermaid' | 'markdown' | 'code_snippet' | 'quote';
export type Role = 'roast_master' | 'wise_sage' | 'chaos_agent';

export interface Block {
  type: BlockType;
  role?: Role;
  lang?: string;
  content: string;
}

export interface Card {
  id: string;
  topic: string;
  tags: string[];
  complexity: number;
  payload: CardPayload;
  created_at: string;
  queue_length?: number;
  needs_replenish?: boolean;
}
