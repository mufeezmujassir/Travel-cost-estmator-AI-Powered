import os
import re
from typing import List, Tuple


class DocRetriever:
    """Lightweight document retriever with FAISS+embeddings if available,
    otherwise falls back to simple keyword search.

    Indexes a curated set of markdown files from the repository and returns
    top-k relevant chunks with their source filenames.
    """

    def __init__(self, project_root: str, documents: List[str], chunk_size: int = 800, chunk_overlap: int = 120):
        self.project_root = project_root
        self.documents = documents
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self._faiss_available = False
        self._index = None
        self._embeddings = None
        self._chunks: List[Tuple[str, str]] = []  # (source, chunk_text)

        self._load_documents()
        self._try_build_faiss()

    def _read_file(self, path: str) -> str:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""

    def _split_into_chunks(self, text: str) -> List[str]:
        chunks: List[str] = []
        start = 0
        while start < len(text):
            end = min(len(text), start + self.chunk_size)
            chunks.append(text[start:end])
            if end == len(text):
                break
            start = max(end - self.chunk_overlap, start + 1)
        return chunks

    def _load_documents(self) -> None:
        for rel_path in self.documents:
            abs_path = os.path.join(self.project_root, rel_path)
            content = self._read_file(abs_path)
            if not content:
                continue
            for chunk in self._split_into_chunks(content):
                self._chunks.append((rel_path, chunk))

    def _try_build_faiss(self) -> None:
        try:
            # Lazy import; optional dependency
            from langchain_community.embeddings import HuggingFaceEmbeddings
            from langchain_community.vectorstores import FAISS
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            self._faiss_available = True

            texts = [chunk for _, chunk in self._chunks]
            metadatas = [{"source": src} for src, _ in self._chunks]

            # Re-split with LC splitter for better boundaries
            splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
            splitted_texts: List[str] = []
            splitted_metas: List[dict] = []
            for meta, text in zip(metadatas, texts):
                parts = splitter.split_text(text)
                for p in parts:
                    splitted_texts.append(p)
                    splitted_metas.append(meta)

            self._embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            self._index = FAISS.from_texts(splitted_texts, self._embeddings, metadatas=splitted_metas)
        except Exception:
            # Fall back to keyword search
            self._faiss_available = False
            self._index = None
            self._embeddings = None

    def retrieve(self, query: str, k: int = 4) -> List[Tuple[str, str]]:
        if not query or not self._chunks:
            return []

        if self._faiss_available and self._index is not None:
            try:
                docs = self._index.similarity_search(query, k=k)
                results: List[Tuple[str, str]] = []
                for d in docs:
                    src = d.metadata.get("source", "")
                    results.append((src, d.page_content))
                return results
            except Exception:
                pass

        # Simple fallback: keyword frequency ranking
        tokens = [t for t in re.split(r"[^\w]+", query.lower()) if t]
        scored: List[Tuple[int, int]] = []  # (score, idx)
        for idx, (_, chunk) in enumerate(self._chunks):
            text_l = chunk.lower()
            score = sum(text_l.count(tok) for tok in tokens)
            if score:
                scored.append((score, idx))
        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:k]
        return [self._chunks[i] for _, i in top]


