import os
import re
import math
from collections import Counter


class VectorStore:
    def __init__(self, knowledge_dir: str = "knowledge_base"):
        self.knowledge_dir = knowledge_dir
        self.chunks = []
        self.vocab = {}
        self.idf = {}
        self.chunk_vectors = []
        self.is_indexed = False

    def load_and_index(self):
        """Loads markdown/text files from knowledge_base, chunks them, and builds a TF-IDF index."""
        self.chunks = []
        if not os.path.exists(self.knowledge_dir):
            self.is_indexed = True
            return

        for root, _, files in os.walk(self.knowledge_dir):
            for file in files:
                if file.endswith((".md", ".txt")):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.knowledge_dir)
                    self._parse_file(file_path, rel_path)

        if self.chunks:
            self._build_tfidf_index()

        self.is_indexed = True

    def _parse_file(self, file_path: str, rel_path: str):
        """Splits markdown file into sections by headers."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

            sections = re.split(r'\n(?=#{1,3}\s)', text)
            for idx, sec in enumerate(sections):
                cleaned = sec.strip()
                if len(cleaned) > 20:
                    first_line = cleaned.split('\n')[0]
                    title = first_line.lstrip('#').strip()
                    self.chunks.append({
                        "id": f"{rel_path}_sec_{idx}",
                        "source": rel_path,
                        "title": title,
                        "content": cleaned
                    })
        except Exception as e:
            print(f"[VectorStore] Error reading {file_path}: {e}")

    def _tokenize(self, text: str) -> list[str]:
        return [w.lower() for w in re.findall(r'\w+', text) if len(w) > 2]

    def _build_tfidf_index(self):
        num_docs = len(self.chunks)
        df = Counter()
        doc_tokens = []

        for chunk in self.chunks:
            tokens = self._tokenize(chunk["content"])
            doc_tokens.append(tokens)
            unique_tokens = set(tokens)
            for token in unique_tokens:
                df[token] += 1

        all_words = list(df.keys())
        self.vocab = {word: idx for idx, word in enumerate(all_words)}
        self.idf = {word: math.log((num_docs + 1) / (count + 1)) + 1 for word, count in df.items()}

        self.chunk_vectors = []
        for tokens in doc_tokens:
            vec = self._vectorize(tokens)
            self.chunk_vectors.append(vec)

    def _vectorize(self, tokens: list[str]) -> dict[int, float]:
        tf = Counter(tokens)
        total_tokens = len(tokens) or 1
        vec = {}
        norm_sq = 0.0

        for word, count in tf.items():
            if word in self.vocab:
                word_id = self.vocab[word]
                tfidf = (count / total_tokens) * self.idf[word]
                vec[word_id] = tfidf
                norm_sq += tfidf ** 2

        norm = math.sqrt(norm_sq) or 1.0
        return {word_id: score / norm for word_id, score in vec.items()}

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        if not self.is_indexed:
            self.load_and_index()

        if not self.chunks:
            return []

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return self.chunks[:top_k]

        query_vec = self._vectorize(query_tokens)

        scores = []
        for idx, chunk_vec in enumerate(self.chunk_vectors):
            dot_product = 0.0
            for word_id, val in query_vec.items():
                if word_id in chunk_vec:
                    dot_product += val * chunk_vec[word_id]
            scores.append((dot_product, idx))

        scores.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, idx in scores[:top_k]:
            if score > 0 or len(results) < top_k:
                chunk = dict(self.chunks[idx])
                chunk["score"] = float(score)
                results.append(chunk)

        return results
