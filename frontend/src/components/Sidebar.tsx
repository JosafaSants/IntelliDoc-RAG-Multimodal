import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, FileText, X, Zap, ChevronDown, Brain, Database, BarChart3 } from "lucide-react";
import type { Document, RagasMetric } from "@/types/chat";

const DEMO_DOCS: Document[] = [
  { id: "1", name: "manual_tecnico_v2.pdf", size: 2400000, chunks: 42, indexed: true },
  { id: "2", name: "api_rest_security.pdf", size: 1800000, chunks: 28, indexed: true },
  { id: "3", name: "git_workflows.pdf", size: 950000, chunks: 15, indexed: true },
];

const DEMO_METRICS: RagasMetric[] = [
  { key: "faithfulness", label: "Fidelidade", score: 0.89, threshold: 0.80 },
  { key: "relevancy", label: "Relevância", score: 0.82, threshold: 0.75 },
  { key: "precision", label: "Precisão Ctx", score: 0.76, threshold: 0.70 },
  { key: "recall", label: "Recall Ctx", score: 0.71, threshold: 0.70 },
];

interface SidebarProps {
  onClose?: () => void;
}

export default function Sidebar({ onClose }: SidebarProps) {
  const [docs, setDocs] = useState<Document[]>(DEMO_DOCS);
  const [isDragOver, setIsDragOver] = useState(false);
  const [systemOpen, setSystemOpen] = useState(false);

  const totalChunks = docs.reduce((a, d) => a + d.chunks, 0);
  const avgScore = DEMO_METRICS.reduce((a, m) => a + m.score, 0) / DEMO_METRICS.length;

  const removeDoc = (id: string) => setDocs((prev) => prev.filter((d) => d.id !== id));

  const getScoreColor = (score: number, threshold: number) => {
    if (score >= threshold) return "text-success";
    if (score >= threshold - 0.1) return "text-warning";
    return "text-destructive";
  };

  const getScoreEmoji = (score: number, threshold: number) => {
    if (score >= threshold) return "🟢";
    if (score >= threshold - 0.1) return "🟡";
    return "🔴";
  };

  return (
    <aside className="w-72 h-screen bg-surface border-r border-border-subtle flex flex-col overflow-hidden">
      {/* Logo */}
      <div className="p-5 border-b border-border-subtle flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-lg bg-primary/15 flex items-center justify-center glow-accent">
            <Brain className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h1 className="font-display text-lg font-bold text-foreground tracking-wide leading-none">
              INTELLIDOC
            </h1>
            <span className="font-display text-[0.6rem] font-semibold text-primary tracking-[0.2em] uppercase">
              RAG
            </span>
          </div>
        </div>
        {/* Close button - mobile only */}
        <button
          onClick={onClose}
          className="md:hidden p-1.5 rounded-md hover:bg-elevated text-text-secondary hover:text-foreground transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-5">
        {/* Upload */}
        <section>
          <h3 className="font-display text-[0.65rem] font-bold text-text-secondary uppercase tracking-[0.15em] mb-3 flex items-center gap-1.5">
            <Upload className="w-3 h-3" /> ENVIAR DOCUMENTOS
          </h3>
          <div
            className={`border border-dashed rounded-lg p-6 text-center transition-all duration-200 cursor-pointer ${
              isDragOver
                ? "border-primary bg-primary/5 glow-accent"
                : "border-border-mid hover:border-primary/50"
            }`}
            onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
            onDragLeave={() => setIsDragOver(false)}
            onDrop={() => setIsDragOver(false)}
          >
            <Upload className="w-5 h-5 mx-auto mb-2 text-text-muted" />
            <p className="text-[0.68rem] text-text-secondary">
              Arraste PDFs ou imagens
            </p>
            <p className="text-[0.6rem] text-text-muted mt-1">
              PDF, PNG, JPG, WEBP
            </p>
          </div>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="mt-3 w-full py-2.5 rounded-md bg-elevated border border-border-mid font-display text-[0.75rem] font-bold text-primary uppercase tracking-wider hover:bg-primary hover:text-primary-foreground hover:glow-accent transition-all duration-200"
          >
            <Zap className="w-3.5 h-3.5 inline mr-1.5 -mt-0.5" />
            Indexar Agora
          </motion.button>
        </section>

        {/* Documents */}
        <section>
          <h3 className="font-display text-[0.65rem] font-bold text-text-secondary uppercase tracking-[0.15em] mb-3 flex items-center gap-1.5">
            <Database className="w-3 h-3" /> DOCUMENTOS ({docs.length})
          </h3>
          <AnimatePresence>
            {docs.map((doc) => (
              <motion.div
                key={doc.id}
                layout
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                className="group flex items-center justify-between py-2 px-2.5 rounded-md hover:bg-elevated/60 transition-colors mb-1"
              >
                <div className="flex items-center gap-2 min-w-0">
                  <FileText className="w-3.5 h-3.5 text-primary/60 shrink-0" />
                  <div className="min-w-0">
                    <p className="text-[0.7rem] text-text-primary truncate max-w-[160px]">
                      {doc.name}
                    </p>
                    <p className="text-[0.58rem] text-text-muted">
                      {doc.chunks} chunks
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => removeDoc(doc.id)}
                  className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-destructive/20 transition-all"
                >
                  <X className="w-3 h-3 text-destructive" />
                </button>
              </motion.div>
            ))}
          </AnimatePresence>
          {docs.length === 0 && (
            <p className="text-[0.65rem] text-text-muted text-center py-4">
              Nenhum documento ainda
            </p>
          )}
        </section>

        {/* System & RAGAS */}
        <section>
          <button
            onClick={() => setSystemOpen(!systemOpen)}
            className="w-full flex items-center justify-between font-display text-[0.65rem] font-bold text-text-secondary uppercase tracking-[0.15em] mb-2 hover:text-primary transition-colors"
          >
            <span className="flex items-center gap-1.5">
              <BarChart3 className="w-3 h-3" /> SISTEMA & RAGAS
            </span>
            <ChevronDown className={`w-3 h-3 transition-transform ${systemOpen ? "rotate-180" : ""}`} />
          </button>

          <AnimatePresence>
            {systemOpen && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="overflow-hidden"
              >
                <div className="grid grid-cols-2 gap-2 mb-3">
                  <div className="bg-elevated border border-border-subtle rounded-lg p-3 text-center">
                    <p className="font-display text-xl font-bold text-primary">{docs.length}</p>
                    <p className="text-[0.58rem] text-text-muted uppercase tracking-wider">PDFs</p>
                  </div>
                  <div className="bg-elevated border border-border-subtle rounded-lg p-3 text-center">
                    <p className="font-display text-xl font-bold text-primary">{totalChunks}</p>
                    <p className="text-[0.58rem] text-text-muted uppercase tracking-wider">Chunks</p>
                  </div>
                </div>

                <div className="space-y-2.5">
                  {DEMO_METRICS.map((m) => (
                    <div key={m.key}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[0.62rem] text-text-secondary">
                          {getScoreEmoji(m.score, m.threshold)} {m.label}
                        </span>
                        <span className={`text-[0.65rem] font-bold font-display ${getScoreColor(m.score, m.threshold)}`}>
                          {m.score.toFixed(2)}
                        </span>
                      </div>
                      <div className="h-1 bg-elevated rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${Math.min(m.score * 100, 100)}%` }}
                          transition={{ duration: 0.8, delay: 0.2 }}
                          className="h-full rounded-full bg-gradient-to-r from-primary to-primary/60"
                        />
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-3 bg-elevated border border-border-subtle rounded-lg p-3 text-center">
                  <p className="text-[0.58rem] text-text-muted uppercase tracking-wider mb-1">Score Médio</p>
                  <p className="font-display text-2xl font-bold text-primary">{avgScore.toFixed(2)}</p>
                  <p className={`text-[0.6rem] font-display font-semibold ${avgScore >= 0.75 ? "text-success" : "text-warning"}`}>
                    {avgScore >= 0.75 ? "✅ Aprovado" : "⚠️ Abaixo do mínimo"}
                  </p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </section>
      </div>
    </aside>
  );
}
