import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Trash2, FileText, Brain, Menu } from "lucide-react";
import type { ChatMessage } from "@/types/chat";
import WelcomeScreen from "./WelcomeScreen";

// Função que chama a API FastAPI real em vez de simular uma resposta
// fetch() é a função nativa do navegador para fazer requisições HTTP
const chamarAPI = async (question: string): Promise<{ content: string; sources: string[] }> => {
  const response = await fetch("http://localhost:8000/chat", {
    method: "POST",                              // Método POST pois estamos enviando dados
    headers: { "Content-Type": "application/json" }, // Informa que o corpo é JSON
    body: JSON.stringify({ pergunta: question }), // Serializa o objeto para string JSON
  });

  if (!response.ok) {
    // Se a API retornar erro (ex: 500), lança uma exceção com a mensagem
    throw new Error(`Erro na API: ${response.status}`);
  }

  const data = await response.json(); // Converte a resposta JSON em objeto JavaScript

  return {
    content: data.resposta,  // Campo "resposta" que definimos no PerguntaResponse do Python
    sources: data.fontes,    // Campo "fontes" que definimos no PerguntaResponse do Python
  };
};

interface ChatAreaProps {
  onMenuClick?: () => void;
}

export default function ChatArea({ onMenuClick }: ChatAreaProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  const handleSend = async (text?: string) => {
    const question = text || input.trim();
    if (!question || isLoading) return;

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: question,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    const result = await chamarAPI(question);

    const assistantMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: "assistant",
      content: result.content,
      sources: result.sources,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, assistantMsg]);
    setIsLoading(false);
  };

  const clearChat = () => setMessages([]);

  return (
    <div className="flex-1 flex flex-col h-screen min-w-0">
      {/* Header */}
      <div className="px-4 sm:px-6 py-3 sm:py-4 border-b border-border-subtle flex items-center justify-between shrink-0 gap-3">
        {/* Mobile menu button */}
        <button
          onClick={onMenuClick}
          className="md:hidden p-2 -ml-1 rounded-lg hover:bg-elevated text-text-secondary hover:text-foreground transition-colors"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="min-w-0 flex-1">
          <h1 className="font-display text-lg sm:text-xl font-bold text-foreground truncate">
            🧠 <span className="text-gradient">IntelliDoc</span>
          </h1>
          <p className="text-[0.6rem] sm:text-[0.65rem] text-text-muted tracking-wide hidden sm:block">
            Sistema RAG Multimodal · Converse com seus documentos técnicos
          </p>
        </div>
        {messages.length > 0 && (
          <motion.button
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={clearChat}
            className="flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-md bg-elevated border border-border-subtle text-[0.7rem] text-text-secondary hover:text-destructive hover:border-destructive/30 transition-all shrink-0"
          >
            <Trash2 className="w-3 h-3" />
            <span className="hidden sm:inline">Limpar</span>
          </motion.button>
        )}
      </div>

      {/* Messages */}
      {messages.length === 0 ? (
        <WelcomeScreen onSuggestionClick={(text) => handleSend(text)} />
      ) : (
        <div ref={scrollRef} className="flex-1 overflow-y-auto px-3 sm:px-6 py-4 space-y-4">
          <AnimatePresence>
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-2 sm:gap-3 ${msg.role === "user" ? "justify-end" : ""}`}
              >
                {msg.role === "assistant" && (
                  <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-primary/15 flex items-center justify-center shrink-0 mt-1">
                    <Brain className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-primary" />
                  </div>
                )}
                <div
                  className={`max-w-[85%] sm:max-w-[70%] rounded-xl px-3 sm:px-4 py-2.5 sm:py-3 ${
                    msg.role === "user"
                      ? "bg-primary/15 border border-primary/20"
                      : "bg-surface border border-border-subtle"
                  }`}
                >
                  <p className="text-[0.78rem] sm:text-[0.82rem] text-foreground leading-relaxed whitespace-pre-wrap">
                    {msg.content}
                  </p>
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-2 sm:mt-3 pt-2 border-t border-border-subtle flex flex-wrap gap-1.5">
                      <span className="text-[0.55rem] sm:text-[0.6rem] text-text-muted mr-1">🔍 Fontes:</span>
                      {msg.sources.map((src) => (
                        <span
                          key={src}
                          className="inline-flex items-center gap-1 px-1.5 sm:px-2 py-0.5 rounded bg-elevated text-[0.55rem] sm:text-[0.6rem] text-text-secondary"
                        >
                          <FileText className="w-2.5 h-2.5" />
                          <span className="truncate max-w-[100px] sm:max-w-none">{src}</span>
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex gap-2 sm:gap-3"
            >
              <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-primary/15 flex items-center justify-center shrink-0">
                <Brain className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-primary animate-pulse" />
              </div>
              <div className="bg-surface border border-border-subtle rounded-xl px-4 py-3">
                <div className="flex gap-1.5">
                  {[0, 1, 2].map((i) => (
                    <motion.div
                      key={i}
                      animate={{ opacity: [0.3, 1, 0.3] }}
                      transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
                      className="w-2 h-2 rounded-full bg-primary"
                    />
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </div>
      )}

      {/* Input */}
      <div className="p-3 sm:p-4 border-t border-border-subtle shrink-0">
        <div className="flex gap-2 max-w-4xl mx-auto">
          <div className="flex-1 relative">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
              placeholder="💬  Pergunte algo..."
              className="w-full bg-surface border border-border-mid rounded-xl px-3 sm:px-4 py-2.5 sm:py-3 text-[0.8rem] sm:text-[0.82rem] text-foreground placeholder:text-text-muted focus:outline-none focus:border-primary focus:glow-accent transition-all font-body"
              disabled={isLoading}
            />
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => handleSend()}
            disabled={!input.trim() || isLoading}
            className="w-10 h-10 sm:w-11 sm:h-11 rounded-xl bg-primary flex items-center justify-center text-primary-foreground disabled:opacity-30 disabled:cursor-not-allowed hover:glow-accent-strong transition-all shrink-0"
          >
            <Send className="w-4 h-4" />
          </motion.button>
        </div>
      </div>
    </div>
  );
}
