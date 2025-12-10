import { Card } from '../types/card';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api';

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

  async getNextCard(): Promise<Card> {
    const response = await fetch(`${API_BASE}/feed/next?user_id=${this.userId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch card');
    }
    return response.json();
  }

  async recordInteraction(cardId: string, action: string, duration?: number) {
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
  }

  async getQueueStatus(): Promise<{ queue_length: number; preview: string[] }> {
    const response = await fetch(`${API_BASE}/feed/queue/status?user_id=${this.userId}`);
    return response.json();
  }

  async getStats(): Promise<any> {
    const response = await fetch(`${API_BASE}/interaction/stats?user_id=${this.userId}`);
    return response.json();
  }
}
