import { Card } from '../types/card';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api';

// 扩展的响应类型，包含生成状态
interface CardResponse extends Card {
  generating?: boolean;
  error?: string;
}

// 自定义错误类，包含状态码
class APIError extends Error {
  status: number;
  
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export class APIService {
  private userId: string;

  constructor() {
    // MVP: 使用 localStorage 存储用户 ID
    this.userId = localStorage.getItem('mindslot_user_id') || this.generateUserId();
  }

  private generateUserId(): string {
    const id = crypto.randomUUID();
    localStorage.setItem('mindslot_user_id', id);
    return id;
  }

  getUserId(): string {
    return this.userId;
  }

  async getNextCard(): Promise<CardResponse> {
    const response = await fetch(`${API_BASE}/feed/next?user_id=${this.userId}`);
    
    // 202 表示正在生成中
    if (response.status === 202) {
      const data = await response.json();
      return { ...data, generating: true } as CardResponse;
    }
    
    if (!response.ok) {
      const error = new APIError('Failed to fetch card', response.status);
      throw error;
    }
    
    return response.json();
  }

  async recordInteraction(cardId: string, action: string, duration?: number) {
    try {
      await fetch(`${API_BASE}/interaction/record`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: this.userId,
          card_id: cardId,
          action,
          duration
        })
      });
    } catch (e) {
      console.error('Failed to record interaction:', e);
    }
  }

  async getQueueStatus(): Promise<{ 
    queue_length: number; 
    preview: string[];
    user_interests?: Record<string, number>;
    preferred_tags?: string[];
  }> {
    const response = await fetch(`${API_BASE}/feed/queue/status?user_id=${this.userId}`);
    return response.json();
  }

  async getStats(): Promise<{
    total_interactions: number;
    total_likes: number;
    total_skips: number;
    total_finished: number;
    avg_duration_ms: number;
    engagement_rate: number;
  }> {
    const response = await fetch(`${API_BASE}/interaction/stats?user_id=${this.userId}`);
    return response.json();
  }

  async getRecommendations(): Promise<{
    interest_weights: Record<string, number>;
    preferred_tags: string[];
    disliked_tags: string[];
    session_context: {
      recent_tags: string[];
      recent_card_ids: string[];
      quick_skipped_tags: string[];
    };
  }> {
    const response = await fetch(`${API_BASE}/feed/recommendations?user_id=${this.userId}`);
    return response.json();
  }

  async triggerGeneration(count: number = 10): Promise<{ status: string; message: string }> {
    const response = await fetch(`${API_BASE}/feed/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        count,
        user_id: this.userId
      })
    });
    return response.json();
  }

  async getPoolStatus(): Promise<{
    total_cards: number;
    tag_distribution: Record<string, number>;
    is_generating: boolean;
  }> {
    const response = await fetch(`${API_BASE}/feed/pool/status`);
    return response.json();
  }
}
