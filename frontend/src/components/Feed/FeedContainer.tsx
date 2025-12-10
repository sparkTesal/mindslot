import React, { useState, useEffect } from 'react';
import { CardRenderer } from '../Card/CardRenderer';
import { APIService } from '../../services/api';
import { Card } from '../../types/card';

const api = new APIService();

export const FeedContainer: React.FC = () => {
  const [currentCard, setCurrentCard] = useState<Card | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [startTime, setStartTime] = useState(Date.now());

  const loadNextCard = async () => {
    setLoading(true);
    setError(null);
    try {
      const card = await api.getNextCard();
      setCurrentCard(card);
      setStartTime(Date.now());
    } catch (error) {
      console.error('Failed to load card:', error);
      setError('无法加载卡片，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

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
          onClick={loadNextCard}
          className="px-6 py-2 bg-cyan-600 rounded hover:bg-cyan-700 transition"
        >
          重试
        </button>
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
