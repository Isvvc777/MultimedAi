import React, { useState, useRef, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { Send, Bot, User, ChevronLeft, Loader2, Sparkles } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const quickChips = [
  "Explain my risk score in simple terms",
  "Translate my lab report to French",
  "What should I ask my doctor?",
  "Are my vital signs normal?"
];

const ChatPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: "Hello! I am your MultiMedAI assistant. I have reviewed your analysis and I'm ready to answer any questions you have about your risk score, uploaded images, lab reports, or vital signs. How can I help you today?" }
  ]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || isStreaming) return;

    const newMessages = [...messages, { role: 'user' as const, content: text }];
    setMessages(newMessages);
    setInput('');
    setIsStreaming(true);

    // Add empty assistant message to be filled via stream
    setMessages((prev) => [...prev, { role: 'assistant', content: '' }]);

    try {
      // Format history for backend
      const history = newMessages
        .filter((_, i) => i !== 0 && i !== newMessages.length - 1) // exclude first welcome and last user message
        .map(m => `${m.role === 'user' ? 'Human' : 'AI'}: ${m.content}`)
        .join('\n');

      const response = await fetch(`http://localhost:8000/api/v1/chat/${id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, history })
      });

      if (!response.body) throw new Error('No response body');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      let assistantText = '';

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          assistantText += chunk;
          
          setMessages((prev) => {
            const updated = [...prev];
            updated[updated.length - 1].content = assistantText;
            return updated;
          });
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1].content += "\n\n*(Error connecting to the AI assistant. Please try again.)*";
        return updated;
      });
    } finally {
      setIsStreaming(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto h-[calc(100vh-8rem)] flex flex-col bg-white rounded-3xl shadow-lg border border-slate-200 overflow-hidden animate-in zoom-in-95 duration-500">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50/50">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate(`/report/${id}`)} className="p-2 hover:bg-slate-200 rounded-full transition-colors text-slate-500">
            <ChevronLeft size={20} />
          </button>
          <div>
            <h2 className="font-bold text-slate-800 flex items-center gap-2">
              <Bot className="text-blue-600" size={20} /> AI Medical Assistant
            </h2>
            <p className="text-xs text-emerald-600 font-medium flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> Online and connected to your report
            </p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/30">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`flex-shrink-0 w-10 h-10 flex items-center justify-center rounded-full shadow-sm ${msg.role === 'user' ? 'bg-blue-600' : 'bg-white border border-slate-200'}`}>
              {msg.role === 'user' ? <User className="text-white" size={20} /> : <Bot className="text-blue-600" size={20} />}
            </div>
            <div className={`max-w-[80%] rounded-2xl p-4 shadow-sm ${msg.role === 'user' ? 'bg-blue-600 text-white rounded-tr-none' : 'bg-white border border-slate-100 rounded-tl-none text-slate-700'}`}>
              {msg.role === 'assistant' ? (
                <div className="prose prose-slate prose-sm max-w-none">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              ) : (
                <p className="whitespace-pre-wrap">{msg.content}</p>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Chips */}
      {messages.length < 3 && (
        <div className="px-6 py-3 flex flex-wrap gap-2 bg-slate-50 border-t border-slate-100">
          <span className="text-xs font-bold text-slate-400 flex items-center gap-1 w-full mb-1"><Sparkles size={12}/> Suggested</span>
          {quickChips.map((chip, idx) => (
            <button 
              key={idx}
              onClick={() => sendMessage(chip)}
              disabled={isStreaming}
              className="text-xs font-medium bg-white border border-slate-200 text-slate-600 px-3 py-1.5 rounded-full hover:border-blue-300 hover:text-blue-600 transition-colors disabled:opacity-50"
            >
              {chip}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="p-4 bg-white border-t border-slate-100">
        <form 
          onSubmit={(e) => { e.preventDefault(); sendMessage(input); }}
          className="flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-full px-4 py-2 focus-within:ring-2 focus-within:ring-blue-500/20 focus-within:border-blue-500 transition-all"
        >
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isStreaming}
            placeholder="Ask anything about your analysis..."
            className="flex-1 bg-transparent border-none focus:outline-none py-2 text-slate-700 disabled:opacity-50"
          />
          <button 
            type="submit" 
            disabled={!input.trim() || isStreaming}
            className="w-10 h-10 flex items-center justify-center rounded-full bg-blue-600 text-white disabled:bg-slate-300 hover:bg-blue-700 transition-colors shadow-sm"
          >
            {isStreaming ? <Loader2 className="animate-spin" size={18} /> : <Send size={18} className="ml-0.5" />}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatPage;
