import React from 'react';
import { motion } from 'framer-motion';
import { Card } from '../../types/card';
import { BlockRenderer } from './BlockRenderer';

interface CardRendererProps {
  card: Card;
  onSwipeUp: () => void;
  onDoubleTap: () => void;
}

export const CardRenderer: React.FC<CardRendererProps> = ({ card, onSwipeUp, onDoubleTap }) => {
  const { payload } = card;
  const [liked, setLiked] = React.useState(false);

  const handleDoubleTap = () => {
    setLiked(true);
    onDoubleTap();
    setTimeout(() => setLiked(false), 1000);
  };

  return (
    <motion.div
      className={`card-container ${payload.style_preset} h-screen w-full overflow-y-auto snap-start relative`}
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -50 }}
      onDoubleClick={handleDoubleTap}
    >
      {/* Like animation */}
      {liked && (
        <motion.div
          className="absolute inset-0 flex items-center justify-center pointer-events-none z-50"
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1.5, opacity: 1 }}
          exit={{ scale: 2, opacity: 0 }}
        >
          <div className="text-6xl">❤️</div>
        </motion.div>
      )}

      <div className="card-content max-w-2xl mx-auto p-6 pb-20">
        {/* Header */}
        <div className="card-header mb-6">
          <h1 className="text-3xl font-bold mb-2 leading-tight">{payload.title}</h1>
          <p className="hook-text text-lg opacity-80 italic mb-3">{payload.hook_text}</p>
          <div className="flex items-center justify-between">
            <div className="tags flex gap-2">
              {card.tags.map((tag, idx) => (
                <span key={idx} className="tag px-2 py-1 bg-cyan-700 rounded text-xs">
                  {tag}
                </span>
              ))}
            </div>
            <div className="complexity text-sm opacity-70">
              {'⭐'.repeat(card.complexity)}
            </div>
          </div>
        </div>

        {/* Blocks */}
        <div className="card-blocks">
          {payload.blocks.map((block, idx) => (
            <BlockRenderer key={idx} block={block} />
          ))}
        </div>

        {/* Footer */}
        <div className="card-footer mt-8 text-center opacity-50 text-sm">
          <p>👆 双击收藏 · 上滑下一张</p>
          {card.queue_length !== undefined && (
            <p className="mt-2 text-xs">队列剩余: {card.queue_length} 张</p>
          )}
        </div>
      </div>
    </motion.div>
  );
};
