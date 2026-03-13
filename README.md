# IntelliDoc-RAG-Multimodal
A "question and answer" system that ingests technical PDFs and images (using OCR with Tesseract). The data is transformed into embeddings, stored in a vector database (Pinecone or Weaviate), and queried via GPT-4. The key difference is the implementation of an evaluation flow to measure the accuracy of the answers and avoid hallucinations.
