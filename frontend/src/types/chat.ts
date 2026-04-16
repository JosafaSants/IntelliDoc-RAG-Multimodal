export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: string[];
  timestamp: Date;
}

export interface Document {
  id: string;
  name: string;
  size: number;
  chunks: number;
  indexed: boolean;
}

export interface RagasMetric {
  key: string;
  label: string;
  score: number;
  threshold: number;
}
