import React from 'react';
import ReactMarkdown from 'react-markdown';
import mermaid from 'mermaid';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Block } from '../../types/card';

mermaid.initialize({ startOnLoad: false, theme: 'dark' });

interface BlockRendererProps {
  block: Block;
}

export const BlockRenderer: React.FC<BlockRendererProps> = ({ block }) => {
  const mermaidRef = React.useRef<HTMLDivElement>(null);
  const [svgContent, setSvgContent] = React.useState<string>('');

  React.useEffect(() => {
    if (block.type === 'mermaid' && mermaidRef.current && block.content) {
      const renderMermaid = async () => {
        try {
          const id = `mermaid-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
          const { svg } = await mermaid.render(id, block.content);
          setSvgContent(svg);
        } catch (err) {
          console.error('Mermaid render error:', err);
          setSvgContent(`<pre style="color: #ff6b6b;">Mermaid 渲染错误: ${err}</pre>`);
        }
      };
      renderMermaid();
    }
  }, [block.content, block.type]);

  switch (block.type) {
    case 'chat_bubble':
      return (
        <div className={`chat-bubble role-${block.role} p-4 rounded-lg my-3 bg-opacity-20 bg-white border-l-4`}>
          {block.role && (
            <div className="role-badge text-xs opacity-70 mb-2 uppercase font-semibold">
              {block.role.replace('_', ' ')}
            </div>
          )}
          <p className="text-base leading-relaxed">{block.content}</p>
        </div>
      );

    case 'mermaid':
      return (
        <div ref={mermaidRef} className="mermaid-container my-4 p-4 bg-black/20 rounded-lg overflow-x-auto">
          {svgContent ? (
            <div dangerouslySetInnerHTML={{ __html: svgContent }} />
          ) : (
            <div className="opacity-50 animate-pulse">加载图表中...</div>
          )}
        </div>
      );

    case 'markdown':
      return (
        <div className="markdown-block my-3 prose prose-inherit max-w-none">
          <ReactMarkdown>{block.content}</ReactMarkdown>
        </div>
      );

    case 'code_snippet':
      return (
        <div className="code-block my-3">
          <SyntaxHighlighter
            language={block.lang || 'javascript'}
            style={vscDarkPlus}
            customStyle={{ borderRadius: '0.5rem', padding: '1rem' }}
          >
            {block.content}
          </SyntaxHighlighter>
        </div>
      );

    case 'quote':
      return (
        <blockquote className="quote-block border-l-4 pl-4 italic my-3 py-2 bg-current/5">
          {block.content}
        </blockquote>
      );

    default:
      return <div className="my-3">{block.content}</div>;
  }
};
