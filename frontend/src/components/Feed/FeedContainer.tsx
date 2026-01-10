import React, { useState, useEffect, useCallback } from 'react';
import { CardRenderer } from '../Card/CardRenderer';
import { APIService } from '../../services/api';
import { Card } from '../../types/card';

const api = new APIService();

// 重试配置
const RETRY_DELAY = 3000;  // 3秒后重试
const MAX_RETRIES = 5;

export const FeedContainer: React.FC = () => {
  const [currentCard, setCurrentCard] = useState<Card | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [startTime, setStartTime] = useState(Date.now());
  const [generating, setGenerating] = useState(false);
  const [retryCount, setRetryCount] = useState(0);

  const loadNextCard = useCallback(async (isRetry = false) => {
    if (!isRetry) {
      setLoading(true);
      setError(null);
      setRetryCount(0);
    }

    try {
      const result = await api.getNextCard();
      
      // 检查是否正在生成中
      if (result.generating) {
        setGenerating(true);
        setLoading(true);
        
        // 自动重试
        if (retryCount < MAX_RETRIES) {
          setTimeout(() => {
            setRetryCount(prev => prev + 1);
            loadNextCard(true);
          }, RETRY_DELAY);
        } else {
          setError('内容生成超时，请稍后再试');
          setLoading(false);
          setGenerating(false);
        }
        return;
      }
      
      setGenerating(false);
      setCurrentCard(result);
      setStartTime(Date.now());
      setLoading(false);
    } catch (error: any) {
      console.error('Failed to load card:', error);
      
      // 检查是否是 202 响应（正在生成）
      if (error.status === 202) {
        setGenerating(true);
        if (retryCount < MAX_RETRIES) {
          setTimeout(() => {
            setRetryCount(prev => prev + 1);
            loadNextCard(true);
          }, RETRY_DELAY);
        } else {
          setError('内容生成超时，请稍后再试');
          setLoading(false);
          setGenerating(false);
        }
        return;
      }
      
      setError('无法加载卡片，请稍后重试');
      setLoading(false);
      setGenerating(false);
    }
  }, [retryCount]);

  const handleSwipeUp = async () => {
    if (!currentCard) return;
    
    const duration = Date.now() - startTime;
    await api.recordInteraction(currentCard.id, 'SKIP', duration);
    loadNextCard();
  };

  const handleDoubleTap = async () => {
    if (!currentCard) return;
    
    await api.recordInteraction(currentCard.id, 'LIKE');
    console.log('Card liked! ❤️');
  };

  useEffect(() => {
    loadNextCard();
  }, []);

  // 键盘快捷键
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === 'ArrowUp' || e.key === ' ') {
        e.preventDefault();
        handleSwipeUp();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [currentCard]);

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-gray-900 text-white">
        <div className="text-xl mb-4">😵 {error}</div>
        <button
          onClick={() => loadNextCard()}
          className="px-6 py-2 bg-cyan-600 rounded hover:bg-cyan-700 transition"
        >
          重试
        </button>
      </div>
    );
  }

  if (generating) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-gray-900 text-white">
        <div className="text-4xl mb-6 animate-bounce">🧠</div>
        <div className="text-xl mb-2">AI 正在生成新内容...</div>
        <div className="text-sm opacity-60">
          正在用 LLM 为你创造新的知识卡片
        </div>
        <div className="mt-4 flex gap-1">
          {[0, 1, 2].map(i => (
            <div
              key={i}
              className="w-3 h-3 bg-cyan-500 rounded-full animate-pulse"
              style={{ animationDelay: `${i * 0.2}s` }}
            />
          ))}
        </div>
        <div className="mt-4 text-xs opacity-40">
          等待中... ({retryCount + 1}/{MAX_RETRIES})
        </div>
      </div>
    );
  }

  if (loading || !currentCard) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-900 text-white">
        <div className="text-xl animate-pulse">Loading...</div>
      </div>
    );
  }

  return (
    <div className="feed-container">
      <CardRenderer
        card={currentCard}
        onSwipeUp={handleSwipeUp}
        onDoubleTap={handleDoubleTap}
      />
      
      {/* Next button */}
      <button
        onClick={handleSwipeUp}
        className="fixed bottom-8 right-8 w-16 h-16 bg-cyan-600 rounded-full flex items-center justify-center text-2xl hover:bg-cyan-700 transition shadow-lg z-10"
        aria-label="Next card"
      >
        ⬆️
      </button>
    </div>
  );
};
