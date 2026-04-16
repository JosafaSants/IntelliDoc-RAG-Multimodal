// ============================================================
// Sidebar.tsx — Painel lateral do IntelliDoc
// Conectado aos endpoints reais da FastAPI:
//   GET  /documentos → lista de arquivos indexados
//   GET  /metricas   → scores RAGAS do último relatório
//   POST /upload     → envia arquivo e dispara ingestão
// ============================================================

import { useState, useEffect, useRef } from "react";
// useRef: referência direta ao elemento <input type="file"> oculto
// necessário para abrir o seletor de arquivos via botão customizado

import { motion, AnimatePresence } from "framer-motion";
import {
  Upload, FileText, X, Zap, ChevronDown,
  Brain, Database, BarChart3, Loader2, CheckCircle, AlertCircle
} from "lucide-react";
// Loader2      → ícone de spinner (animado com spin)
// CheckCircle  → ícone de sucesso
// AlertCircle  → ícone de erro

import type { Document, RagasMetric } from "@/types/chat";

// ============================================================
// CONSTANTES
// ============================================================

// Lê a URL da API da variável de ambiente Vite
// Em desenvolvimento: usa http://localhost:8000 como fallback
// Em produção: defina VITE_API_URL no ambiente de deploy
const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

// Extensões aceitas pelo backend — espelha EXTENSOES_IMAGEM do api.py
const EXTENSOES_ACEITAS = ".pdf,.png,.jpg,.jpeg,.bmp,.tiff,.webp";

// ============================================================
// TIPOS
// ============================================================

interface DocumentoAPI {
  nome: string;
  tipo: "pdf" | "imagem";
}

interface MetricasAPI {
  Faithfulness: number;
  "Answer Relevancy": number;
  "Context Precision": number;
  "Context Recall": number;
  media_geral: number;
}

// Status possíveis do upload — controla o feedback visual
type UploadStatus =
  | { tipo: "idle" }
  | { tipo: "enviando"; nome: string }
  | { tipo: "indexando"; nome: string }
  | { tipo: "ja_indexado"; nome: string }
  | { tipo: "erro"; mensagem: string };

// ============================================================
// MAPEAMENTO API → DISPLAY
// ============================================================

function mapearMetricas(api: MetricasAPI): RagasMetric[] {
  return [
    { key: "faithfulness", label: "Fidelidade",   score: api.Faithfulness          ?? 0, threshold: 0.80 },
    { key: "relevancy",    label: "Relevância",    score: api["Answer Relevancy"]   ?? 0, threshold: 0.75 },
    { key: "precision",    label: "Precisão Ctx",  score: api["Context Precision"]  ?? 0, threshold: 0.70 },
    { key: "recall",       label: "Recall Ctx",    score: api["Context Recall"]     ?? 0, threshold: 0.70 },
  ];
}

// ============================================================
// PROPS
// ============================================================

interface SidebarProps {
  onClose?: () => void;
}

// ============================================================
// COMPONENTE
// ============================================================

export default function Sidebar({ onClose }: SidebarProps) {

  // ── Estado: dados da API ──────────────────────────────────
  const [docs,     setDocs]     = useState<Document[]>([]);
  const [metrics,  setMetrics]  = useState<RagasMetric[]>([]);
  const [avgScore, setAvgScore] = useState<number>(0);
  const [loading,  setLoading]  = useState<boolean>(true);

  // ── Estado: UI ───────────────────────────────────────────
  const [isDragOver,  setIsDragOver]  = useState(false);
  const [systemOpen,  setSystemOpen]  = useState(false);
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>({ tipo: "idle" });

  // ── Ref: input file oculto ────────────────────────────────
  // Usamos um <input type="file"> invisível e disparamos o
  // clique nele quando o usuário clica em "Indexar Agora"
  const inputRef = useRef<HTMLInputElement>(null);

  // ── Efeito: carrega dados ao montar ───────────────────────
  useEffect(() => {
    buscarDados();
  }, []);

  // ============================================================
  // FUNÇÕES DE DADOS
  // ============================================================

  async function buscarDados() {
    try {
      setLoading(true);
      const [resDoc, resMet] = await Promise.all([
        fetch(`${API_BASE}/documentos`),
        fetch(`${API_BASE}/metricas`),
      ]);
      const dadosDoc = await resDoc.json();
      const dadosMet: MetricasAPI = await resMet.json();

      setDocs(
        dadosDoc.documentos.map((doc: DocumentoAPI, i: number) => ({
          id:      String(i + 1),
          name:    doc.nome,
          size:    0,
          chunks:  0,
          indexed: true,
        }))
      );
      setMetrics(mapearMetricas(dadosMet));
      setAvgScore(dadosMet.media_geral ?? 0);
    } catch (erro) {
      console.error("Erro ao buscar dados da API:", erro);
    } finally {
      setLoading(false);
    }
  }

  // ============================================================
  // FUNÇÕES DE UPLOAD
  // ============================================================

  async function enviarArquivo(arquivo: File) {
    // ── 1. Feedback imediato: "enviando" ─────────────────────
    setUploadStatus({ tipo: "enviando", nome: arquivo.name });

    try {
      // ── 2. Monta o FormData — formato que o FastAPI espera ──
      // FormData serializa o arquivo como multipart/form-data
      // O campo deve se chamar "arquivo" — igual ao parâmetro
      // definido no endpoint: arquivo: UploadFile = File(...)
      const formData = new FormData();
      formData.append("arquivo", arquivo);

      // ── 3. Envia para POST /upload ──────────────────────────
      const resposta = await fetch(`${API_BASE}/upload`, {
        method: "POST",
        body: formData,
        // NÃO definimos Content-Type manualmente — o browser
        // define automaticamente com o boundary correto para
        // multipart/form-data quando usamos FormData
      });

      if (!resposta.ok) {
        // Erro HTTP (ex: 400 tipo não suportado)
        const erro = await resposta.json();
        setUploadStatus({ tipo: "erro", mensagem: erro.detail ?? "Erro desconhecido" });
        return;
      }

      const resultado = await resposta.json();

      // ── 4. Atualiza o status conforme a resposta ────────────
      if (resultado.status === "ja_indexado") {
        setUploadStatus({ tipo: "ja_indexado", nome: arquivo.name });
      } else {
        // status === "indexando" — backend processando em background
        setUploadStatus({ tipo: "indexando", nome: arquivo.name });

        // Aguarda 3 segundos e recarrega a lista de documentos
        // para refletir o arquivo recém-indexado na sidebar
        setTimeout(() => {
          buscarDados();
          setUploadStatus({ tipo: "idle" });
        }, 3000);
        return;
      }
    } catch (erro) {
      // Erro de rede (API offline, CORS etc.)
      setUploadStatus({ tipo: "erro", mensagem: "Não foi possível conectar à API." });
    }

    // Limpa o status após 3 segundos (para casos não-indexando)
    setTimeout(() => setUploadStatus({ tipo: "idle" }), 3000);
  }

  // ── Handler: drop de arquivo na zona ─────────────────────
  function handleDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setIsDragOver(false);

    // dataTransfer.files contém os arquivos arrastados
    const arquivo = e.dataTransfer.files[0];
    if (arquivo) enviarArquivo(arquivo);
  }

  // ── Handler: seleção via input file oculto ────────────────
  function handleInputChange(e: React.ChangeEvent<HTMLInputElement>) {
    const arquivo = e.target.files?.[0];
    if (arquivo) enviarArquivo(arquivo);

    // Limpa o valor do input para que o mesmo arquivo
    // possa ser selecionado novamente se necessário
    e.target.value = "";
  }

  // ── Handler: clique no botão "Indexar Agora" ─────────────
  function handleIndexarClick() {
    // Dispara o clique no input file oculto
    inputRef.current?.click();
  }

  // ── Estado: controla qual documento está sendo deletado ───
  // Guarda o id do documento em processo de deleção para
  // desabilitar o botão ✕ e evitar cliques múltiplos
  const [deletandoId, setDeletandoId] = useState<string | null>(null);

  // ── Handler: remove documento do Pinecone + lista visual ──
  async function removeDoc(id: string) {
    // Bloqueia se já há uma deleção em andamento
    if (deletandoId) return;

    const doc = docs.find((d) => d.id === id);
    if (!doc) return;

    setDeletandoId(id); // Marca este documento como "deletando"

    try {
      const resposta = await fetch(`${API_BASE}/documentos/${encodeURIComponent(doc.name)}`, {
        method: "DELETE",
      });

      if (!resposta.ok) {
        const erro = await resposta.json();
        console.error("Erro ao deletar:", erro.detail);
        return;
      }

      // Remove da lista visual só após confirmação da API
      setDocs((prev) => prev.filter((d) => d.id !== id));

    } catch (erro) {
      console.error("Erro de rede ao deletar documento:", erro);
    } finally {
      // Sempre libera o bloqueio, mesmo se der erro
      setDeletandoId(null);
    }
  }

  // ============================================================
  // HELPERS VISUAIS
  // ============================================================

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

  const totalChunks = docs.reduce((a, d) => a + d.chunks, 0);

  // ============================================================
  // RENDERIZAÇÃO DO FEEDBACK DE UPLOAD
  // ============================================================

  function renderUploadStatus() {
    // Não renderiza nada quando está ocioso
    if (uploadStatus.tipo === "idle") return null;

    // Mapeia cada status para ícone + cor + mensagem
    const config = {
      enviando:    { icon: <Loader2 className="w-3 h-3 animate-spin" />, cor: "text-primary",     texto: `Enviando ${uploadStatus.tipo !== "idle" && "nome" in uploadStatus ? uploadStatus.nome : ""}...` },
      indexando:   { icon: <Loader2 className="w-3 h-3 animate-spin" />, cor: "text-primary",     texto: `Indexando ${"nome" in uploadStatus ? uploadStatus.nome : ""}...` },
      ja_indexado: { icon: <CheckCircle className="w-3 h-3" />,          cor: "text-success",     texto: `Já indexado` },
      erro:        { icon: <AlertCircle className="w-3 h-3" />,          cor: "text-destructive", texto: "mensagem" in uploadStatus ? uploadStatus.mensagem : "Erro" },
    }[uploadStatus.tipo];

    return (
      <motion.div
        initial={{ opacity: 0, y: -4 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0 }}
        className={`mt-2 flex items-center gap-1.5 text-[0.65rem] ${config.cor}`}
      >
        {config.icon}
        <span>{config.texto}</span>
      </motion.div>
    );
  }

  // ============================================================
  // RENDERIZAÇÃO PRINCIPAL
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

          {/* Input file oculto — acionado pelo botão abaixo */}
          <input
            ref={inputRef}
            type="file"
            accept={EXTENSOES_ACEITAS}
            onChange={handleInputChange}
            className="hidden"
          />

          {/* Zona de drag-and-drop */}
          <div
            className={`border border-dashed rounded-lg p-6 text-center transition-all duration-200 cursor-pointer ${
              isDragOver
                ? "border-primary bg-primary/5 glow-accent"
                : "border-border-mid hover:border-primary/50"
            }`}
            onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
            onDragLeave={() => setIsDragOver(false)}
            onDrop={handleDrop}
            onClick={handleIndexarClick}
          >
            <Upload className="w-5 h-5 mx-auto mb-2 text-text-muted" />
            <p className="text-[0.68rem] text-text-secondary">
              Arraste PDFs ou imagens
            </p>
            <p className="text-[0.6rem] text-text-muted mt-1">
              PDF, PNG, JPG, WEBP
            </p>
          </div>

          {/* Botão "Indexar Agora" — abre o seletor de arquivos */}
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleIndexarClick}
            disabled={uploadStatus.tipo === "enviando" || uploadStatus.tipo === "indexando"}
            className="mt-3 w-full py-2.5 rounded-md bg-elevated border border-border-mid font-display text-[0.75rem] font-bold text-primary uppercase tracking-wider hover:bg-primary hover:text-primary-foreground hover:glow-accent transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploadStatus.tipo === "enviando" || uploadStatus.tipo === "indexando" ? (
              <Loader2 className="w-3.5 h-3.5 inline mr-1.5 -mt-0.5 animate-spin" />
            ) : (
              <Zap className="w-3.5 h-3.5 inline mr-1.5 -mt-0.5" />
            )}
            {uploadStatus.tipo === "enviando" ? "Enviando..." :
             uploadStatus.tipo === "indexando" ? "Indexando..." :
             "Indexar Agora"}
          </motion.button>

          {/* Feedback de status do upload */}
          <AnimatePresence>
            {renderUploadStatus()}
          </AnimatePresence>
        </section>

        {/* ── Lista de documentos ── */}
        <section>
          <h3 className="font-display text-[0.65rem] font-bold text-text-secondary uppercase tracking-[0.15em] mb-3 flex items-center gap-1.5">
            <Database className="w-3 h-3" /> DOCUMENTOS ({docs.length})
          </h3>

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
                    <p className="text-[0.7rem] text-text-primary truncate max-w-[160px]">
                      {doc.name}
                    </p>
                    <p className="text-[0.58rem] text-text-muted">
                      indexado ✓
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => removeDoc(doc.id)}
                  disabled={deletandoId === doc.id}
                  className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-destructive/20 transition-all disabled:opacity-30 disabled:cursor-not-allowed"
                >
                  {deletandoId === doc.id
                    ? <Loader2 className="w-3 h-3 text-destructive animate-spin" />
                    : <X className="w-3 h-3 text-destructive" />
                  }
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
                <div className="grid grid-cols-2 gap-2 mb-3">
                  <div className="bg-elevated border border-border-subtle rounded-lg p-3 text-center">
                    <p className="font-display text-xl font-bold text-primary">{docs.length}</p>
                    <p className="text-[0.58rem] text-text-muted uppercase tracking-wider">Docs</p>
                  </div>
                  <div className="bg-elevated border border-border-subtle rounded-lg p-3 text-center">
                    <p className="font-display text-xl font-bold text-primary">{totalChunks || "—"}</p>
                    <p className="text-[0.58rem] text-text-muted uppercase tracking-wider">Chunks</p>
                  </div>
                </div>

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