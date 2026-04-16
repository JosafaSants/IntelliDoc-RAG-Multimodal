import { motion } from "framer-motion";
import { Lightbulb, Shield, GitBranch, Binary, BarChart3 } from "lucide-react";

const SUGGESTIONS = [
  { icon: Lightbulb, text: "O que é RAG e como funciona?" },
  { icon: Shield, text: "Boas práticas de segurança em APIs REST?" },
  { icon: GitBranch, text: "Como o Git ajuda no desenvolvimento?" },
  { icon: Binary, text: "O que são embeddings e para que servem?" },
  { icon: BarChart3, text: "Quais métricas o RAGAS utiliza?" },
];

interface Props {
  onSuggestionClick: (text: string) => void;
}

export default function WelcomeScreen({ onSuggestionClick }: Props) {
  return (
    <div className="flex-1 flex items-center justify-center p-4 sm:p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-lg w-full"
      >
        <div className="bg-surface border border-border-subtle rounded-2xl p-6 sm:p-10 text-center glow-accent">
          {/* Animated brain icon */}
          <motion.div
            animate={{ y: [0, -6, 0] }}
            transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
            className="w-12 h-12 sm:w-16 sm:h-16 mx-auto mb-4 sm:mb-5 rounded-xl sm:rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center"
          >
            <span className="text-2xl sm:text-3xl">🧠</span>
          </motion.div>

          <h2 className="font-display text-xl sm:text-2xl font-bold text-foreground mb-2">
            Bem-vindo ao <span className="text-gradient">IntelliDoc</span>
          </h2>
          <p className="text-[0.75rem] sm:text-[0.8rem] text-text-secondary leading-relaxed mb-6 sm:mb-8">
            Envie seus PDFs técnicos e faça perguntas
            sobre o conteúdo usando linguagem natural.
          </p>

          <div className="space-y-2">
            {SUGGESTIONS.map((s, i) => (
              <motion.button
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + i * 0.08 }}
                whileHover={{ x: 4 }}
                onClick={() => onSuggestionClick(s.text)}
                className="w-full flex items-center gap-2.5 sm:gap-3 px-3 sm:px-4 py-2.5 sm:py-3 rounded-lg bg-background border border-border-subtle text-left text-[0.72rem] sm:text-[0.76rem] text-text-secondary hover:border-primary/40 hover:text-foreground transition-all duration-200 group"
              >
                <s.icon className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-text-muted group-hover:text-primary transition-colors shrink-0" />
                {s.text}
              </motion.button>
            ))}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
