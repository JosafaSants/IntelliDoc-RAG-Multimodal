// ============================================================
// ChatArea.tsx — Área principal de chat do IntelliDoc
// Conectado ao endpoint real da FastAPI:
//   POST /chat → recebe pergunta, retorna resposta + fontes
// ============================================================

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Trash2, FileText, Brain, Menu } from "lucide-react";
import type { ChatMessage } from "@/types/chat";
import WelcomeScreen from "./WelcomeScreen";

// ============================================================
// CONFIGURAÇÃO DA API
// ============================================================

// Lê a URL da API da variável de ambiente Vite
// Em desenvolvimento: usa http://localhost:8000 como fallback
// Em produção: defina VITE_API_URL no arquivo frontend/.env
const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

// ============================================================
// FUNÇÃO DE CHAMADA À API
// ============================================================

// Função que chama o endpoint POST /chat da FastAPI
// Separada do componente para facilitar manutenção e testes
const chamarAPI = async (
  question: string
): Promise<{ content: string; sources: string[] }> => {

  // fetch() é a função nativa do navegador para requisições HTTP
  const response = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pergunta: question }),
  });

  if (!response.ok) {
    // Se a API retornar erro (ex: 500), lança exceção com o status
    throw new Error(`Erro na API: ${response.status}`);
  }

  const data = await response.json();

  return {
    content: data.resposta, // Campo definido em PerguntaResponse no Python
    sources: data.fontes,   // Campo definido em PerguntaResponse no Python
  };
};

// ============================================================
// PROPS
// ============================================================

interface ChatAreaProps {
  onMenuClick?: () => void;
}

// ============================================================
// COMPONENTE
// ============================================================

export default function ChatArea({ onMenuClick }: ChatAreaProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input,     setInput]     = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // ── Carrega o histórico do backend ao abrir a página ──────
  // GET /historico retorna as últimas 20 mensagens do SQLite
  // Converte o formato da API para o formato ChatMessage do React
  useEffect(() => {
    const carregarHistorico = async () => {
      try {
        const response = await fetch(`${API_BASE}/historico?limite=20`);
        if (!response.ok) return;

        const data = await response.json();

        // Converte cada entrada do histórico em dois ChatMessages:
        // um para o usuário e um para o assistente
        const msgs: ChatMessage[] = [];
        for (const entrada of data.historico) {
          msgs.push({
            id:        crypto.randomUUID(),
            role:      "user",
            content:   entrada.pergunta,
            timestamp: new Date(entrada.criado_em),
          });
          msgs.push({
            id:        crypto.randomUUID(),
            role:      "assistant",
            content:   entrada.resposta,
            sources:   entrada.fontes,
            timestamp: new Date(entrada.criado_em),
          });
        }
        setMessages(msgs);
      } catch (e) {
        // Falha silenciosa — histórico não é crítico para o app funcionar
        console.warn("Não foi possível carregar o histórico:", e);
      }
    };

    carregarHistorico();
  }, []); // [] = executa apenas uma vez ao montar o componente

  // Rola para o final sempre que uma nova mensagem chega
  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  // ============================================================
  // HANDLER DE ENVIO
  // ============================================================

  const handleSend = async (text?: string) => {
    const question = text || input.trim();
    if (!question || isLoading) return;

    // Adiciona a mensagem do usuário imediatamente na tela
    const userMsg: ChatMessage = {
      id:        crypto.randomUUID(),
      role:      "user",
      content:   question,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      // ── Chama a API e aguarda a resposta ──────────────────
      const result = await chamarAPI(question);

      const assistantMsg: ChatMessage = {
        id:        crypto.randomUUID(),
        role:      "assistant",
        content:   result.content,
        sources:   result.sources,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMsg]);

    } catch (erro) {
      // ── Exibe mensagem de erro no chat (não trava o input) ─
      // Sem este bloco, qualquer falha de rede deixava isLoading
      // em true para sempre — o usuário precisaria recarregar a página
      console.error("Erro ao chamar a API:", erro);

      const erroMsg: ChatMessage = {
        id:        crypto.randomUUID(),
        role:      "assistant",
        content:   "⚠️ Não foi possível conectar à API. Verifique se o servidor está rodando e tente novamente.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, erroMsg]);

    } finally {
      // ── Sempre libera o input, mesmo se der erro ──────────
      // finally executa independente de sucesso ou falha
      setIsLoading(false);
    }
  };

  const clearChat = async () => {
    // Apaga o histórico no backend antes de limpar a tela
    // Se a API falhar, limpa a tela mesmo assim (UX > consistência aqui)
    try {
      await fetch(`${API_BASE}/historico`, { method: "DELETE" });
    } catch (e) {
      console.warn("Não foi possível limpar o histórico no backend:", e);
    }
    setMessages([]);
  };

  // ============================================================
  // RENDERIZAÇÃO
  // ============================================================

  return (
    <div className="flex-1 flex flex-col h-screen min-w-0">

      {/* ── Header ── */}
      <div className="px-4 sm:px-6 py-3 sm:py-4 border-b border-border-subtle flex items-center justify-between shrink-0 gap-3">
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

      {/* ── Mensagens ── */}
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

          {/* Indicador de carregamento */}
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

      {/* ── Input ── */}
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