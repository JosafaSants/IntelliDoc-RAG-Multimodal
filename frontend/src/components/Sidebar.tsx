// ============================================================
// Sidebar.tsx — Painel lateral do IntelliDoc
// Conectado aos endpoints reais da FastAPI:
//   GET /documentos → lista de arquivos indexados
//   GET /metricas   → scores RAGAS do último relatório
// ============================================================

import { useState, useEffect } from "react";
// useEffect: executa código quando o componente é montado
// (é aqui que faremos os fetch para a API)

import { motion, AnimatePresence } from "framer-motion";
import { Upload, FileText, X, Zap, ChevronDown, Brain, Database, BarChart3 } from "lucide-react";
import type { Document, RagasMetric } from "@/types/chat";

// ============================================================
// CONSTANTES DE CONFIGURAÇÃO
// ============================================================

// URL base da FastAPI — se mudar a porta, muda só aqui
const API_BASE = "http://localhost:8000";

// ============================================================
// TIPOS LOCAIS
// ============================================================

// Formato exato que o endpoint GET /documentos retorna
// { "documentos": [{ "nome": "arquivo.pdf", "tipo": "pdf" }] }
interface DocumentoAPI {
  nome: string;
  tipo: "pdf" | "imagem";
}

// Formato exato que o endpoint GET /metricas retorna
// As chaves têm espaços — ex: "Answer Relevancy"
interface MetricasAPI {
  Faithfulness: number;
  "Answer Relevancy": number;
  "Context Precision": number;
  "Context Recall": number;
  media_geral: number;
}

// ============================================================
// MAPEAMENTO: API → DISPLAY
// ============================================================

// Converte o objeto de métricas da API (chaves com espaços)
// para o array que o componente de barras já sabe renderizar
function mapearMetricas(api: MetricasAPI): RagasMetric[] {
  return [
    {
      key: "faithfulness",
      label: "Fidelidade",
      score: api.Faithfulness ?? 0,        // ?? 0 → usa 0 se vier undefined
      threshold: 0.80,
    },
    {
      key: "relevancy",
      label: "Relevância",
      score: api["Answer Relevancy"] ?? 0, // chave com espaço → notação de colchetes
      threshold: 0.75,
    },
    {
      key: "precision",
      label: "Precisão Ctx",
      score: api["Context Precision"] ?? 0,
      threshold: 0.70,
    },
    {
      key: "recall",
      label: "Recall Ctx",
      score: api["Context Recall"] ?? 0,
      threshold: 0.70,
    },
  ];
}

// ============================================================
// PROPS DO COMPONENTE
// ============================================================

interface SidebarProps {
  onClose?: () => void;
}

// ============================================================
// COMPONENTE PRINCIPAL
// ============================================================

export default function Sidebar({ onClose }: SidebarProps) {

  // ----------------------------------------------------------
  // ESTADO: documentos carregados da API
  // Começa como array vazio — preenchido pelo useEffect abaixo
  // ----------------------------------------------------------
  const [docs, setDocs] = useState<Document[]>([]);

  // ----------------------------------------------------------
  // ESTADO: métricas RAGAS carregadas da API
  // Começa como array vazio — preenchido pelo useEffect abaixo
  // ----------------------------------------------------------
  const [metrics, setMetrics] = useState<RagasMetric[]>([]);

  // ----------------------------------------------------------
  // ESTADO: score médio calculado a partir da API
  // Usamos o campo media_geral que já vem calculado pelo backend
  // ----------------------------------------------------------
  const [avgScore, setAvgScore] = useState<number>(0);

  // ----------------------------------------------------------
  // ESTADO: controla se a API está carregando (para feedback visual)
  // ----------------------------------------------------------
  const [loading, setLoading] = useState<boolean>(true);

  // ----------------------------------------------------------
  // ESTADO: drag-and-drop e painel recolhível
  // ----------------------------------------------------------
  const [isDragOver, setIsDragOver] = useState(false);
  const [systemOpen, setSystemOpen] = useState(false);

  // ----------------------------------------------------------
  // EFEITO: busca documentos e métricas ao montar o componente
  // O array vazio [] como segundo argumento significa:
  // "execute isso UMA VEZ, quando o Sidebar aparecer na tela"
  // ----------------------------------------------------------
  useEffect(() => {
    buscarDados();
  }, []);

  // ----------------------------------------------------------
  // FUNÇÃO: faz os dois fetch em paralelo com Promise.all
  // Promise.all espera os dois terminarem antes de atualizar
  // o estado — evita dois re-renders separados
  // ----------------------------------------------------------
  async function buscarDados() {
    try {
      setLoading(true);

      // Dispara os dois fetch ao mesmo tempo (paralelo)
      const [resDocumentos, resMetricas] = await Promise.all([
        fetch(`${API_BASE}/documentos`),
        fetch(`${API_BASE}/metricas`),
      ]);

      // Converte as respostas HTTP para objetos JavaScript
      const dadosDocumentos = await resDocumentos.json();
      const dadosMetricas: MetricasAPI = await resMetricas.json();

      // ----------------------------------------------------------
      // DOCUMENTOS: converte DocumentoAPI[] → Document[]
      // O tipo Document (de @/types/chat) espera id, name, size,
      // chunks e indexed — adaptamos o que a API fornece
      // ----------------------------------------------------------
      const documentosConvertidos: Document[] = dadosDocumentos.documentos.map(
        (doc: DocumentoAPI, index: number) => ({
          id: String(index + 1),   // Gera id sequencial (1, 2, 3...)
          name: doc.nome,          // Nome real do arquivo
          size: 0,                 // API não fornece tamanho — usamos 0
          chunks: 0,               // API não fornece chunks — usamos 0
          indexed: true,           // Se está no controle_ingestao, já foi indexado
        })
      );

      // ----------------------------------------------------------
      // MÉTRICAS: usa a função de mapeamento que criamos acima
      // ----------------------------------------------------------
      const metricasConvertidas = mapearMetricas(dadosMetricas);

      // Atualiza os três estados de uma vez
      setDocs(documentosConvertidos);
      setMetrics(metricasConvertidas);
      setAvgScore(dadosMetricas.media_geral ?? 0);

    } catch (erro) {
      // Se a API estiver offline, loga no console sem travar a UI
      // O usuário vê a lista vazia — sem crash
      console.error("Erro ao buscar dados da API:", erro);
    } finally {
      // Sempre desliga o loading, mesmo se der erro
      setLoading(false);
    }
  }

  // ----------------------------------------------------------
  // COMPUTED: total de chunks (0 por enquanto — API não fornece)
  // Mantemos a lógica para quando o backend enviar esse dado
  // ----------------------------------------------------------
  const totalChunks = docs.reduce((a, d) => a + d.chunks, 0);

  // ----------------------------------------------------------
  // HELPERS: cor e emoji baseados no score vs threshold
  // ----------------------------------------------------------
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

  // ----------------------------------------------------------
  // HANDLER: remove documento da lista LOCAL (só visual por ora)
  // O endpoint DELETE /documentos/{nome} será implementado depois
  // ----------------------------------------------------------
  const removeDoc = (id: string) =>
    setDocs((prev) => prev.filter((d) => d.id !== id));

  // ============================================================
  // RENDERIZAÇÃO
  // ============================================================
  return (
    <aside className="w-72 h-screen bg-surface border-r border-border-subtle flex flex-col overflow-hidden">

      {/* ── Logo ── */}
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
        {/* Botão fechar — visível só no mobile */}
        <button
          onClick={onClose}
          className="md:hidden p-1.5 rounded-md hover:bg-elevated text-text-secondary hover:text-foreground transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-5">

        {/* ── Upload ── */}
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

        {/* ── Lista de documentos ── */}
        <section>
          <h3 className="font-display text-[0.65rem] font-bold text-text-secondary uppercase tracking-[0.15em] mb-3 flex items-center gap-1.5">
            <Database className="w-3 h-3" /> DOCUMENTOS ({docs.length})
          </h3>

          {/* Feedback visual enquanto a API carrega */}
          {loading && (
            <p className="text-[0.65rem] text-text-muted text-center py-4 animate-pulse">
              Carregando...
            </p>
          )}

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
                    {/* Nome do arquivo vindo da API */}
                    <p className="text-[0.7rem] text-text-primary truncate max-w-[160px]">
                      {doc.name}
                    </p>
                    {/* Tipo vindo da API (pdf ou imagem) */}
                    <p className="text-[0.58rem] text-text-muted">
                      indexado ✓
                    </p>
                  </div>
                </div>
                {/* Botão ✕ — remove da lista local por ora */}
                <button
                  onClick={() => removeDoc(doc.id)}
                  className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-destructive/20 transition-all"
                >
                  <X className="w-3 h-3 text-destructive" />
                </button>
              </motion.div>
            ))}
          </AnimatePresence>

          {!loading && docs.length === 0 && (
            <p className="text-[0.65rem] text-text-muted text-center py-4">
              Nenhum documento ainda
            </p>
          )}
        </section>

        {/* ── Sistema & RAGAS ── */}
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
                {/* Cards de contagem */}
                <div className="grid grid-cols-2 gap-2 mb-3">
                  <div className="bg-elevated border border-border-subtle rounded-lg p-3 text-center">
                    {/* Número real de documentos da API */}
                    <p className="font-display text-xl font-bold text-primary">{docs.length}</p>
                    <p className="text-[0.58rem] text-text-muted uppercase tracking-wider">Docs</p>
                  </div>
                  <div className="bg-elevated border border-border-subtle rounded-lg p-3 text-center">
                    <p className="font-display text-xl font-bold text-primary">{totalChunks || "—"}</p>
                    <p className="text-[0.58rem] text-text-muted uppercase tracking-wider">Chunks</p>
                  </div>
                </div>

                {/* Barras de métricas RAGAS vindas da API */}
                <div className="space-y-2.5">
                  {metrics.map((m) => (
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

                {/* Score médio vindo diretamente do campo media_geral da API */}
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