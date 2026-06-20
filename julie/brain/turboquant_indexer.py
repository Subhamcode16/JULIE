"""TurboQuant-inspired local vector search and indexing for Obsidian Vault."""

import os
import glob
import numpy as np
from loguru import logger
from sentence_transformers import SentenceTransformer

OBSIDIAN_VAULT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "obsidian_vault")

# Load a lightweight CPU-friendly embedding model
# all-MiniLM-L6-v2 produces 384-dimensional vectors
_model = None

def get_model():
    global _model
    if _model is None:
        logger.info("Loading sentence-transformers model (this happens once)...")
        _model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
    return _model

class QuantizedIndex:
    """A lightweight vector index using simple INT8 quantization (TurboQuant principles)."""
    
    def __init__(self):
        self.vectors_int8 = []
        self.metadata = []
        self.scale_factors = []
        
    def add_document(self, text: str, meta: dict):
        """Embed, quantize, and add a document to the index."""
        model = get_model()
        vec = model.encode(text)
        
        # Simple symmetric quantization to Int8 to simulate compressed KV cache/Vector DB
        max_val = np.max(np.abs(vec))
        scale = max_val / 127.0 if max_val > 0 else 1.0
        
        vec_int8 = np.round(vec / scale).astype(np.int8)
        
        self.vectors_int8.append(vec_int8)
        self.scale_factors.append(scale)
        self.metadata.append(meta)

    def search(self, query: str, top_k: int = 3) -> list:
        """Search the quantized index."""
        if not self.vectors_int8:
            return []
            
        model = get_model()
        query_vec = model.encode(query)
        
        # Dequantize for dot product
        results = []
        for i, vec_int8 in enumerate(self.vectors_int8):
            scale = self.scale_factors[i]
            dequantized_vec = vec_int8.astype(np.float32) * scale
            
            # Cosine similarity (since model vectors are already normalized)
            score = np.dot(query_vec, dequantized_vec)
            results.append((score, self.metadata[i]))
            
        results.sort(key=lambda x: x[0], reverse=True)
        return results[:top_k]

# Global index instance
_index = QuantizedIndex()

def reindex_vault():
    """Read all markdown files in Obsidian vault and index them."""
    global _index
    _index = QuantizedIndex()
    
    if not os.path.exists(OBSIDIAN_VAULT_DIR):
        return
        
    md_files = glob.glob(os.path.join(OBSIDIAN_VAULT_DIR, "*.md"))
    for file_path in md_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Index the whole file content
            meta = {"file": os.path.basename(file_path), "content": content}
            _index.add_document(content, meta)
        except Exception as e:
            logger.error(f"Error indexing {file_path}: {e}")
            
    logger.info(f"Reindexed {len(_index.vectors_int8)} documents from Obsidian Vault using TurboQuant principles.")

def search_memory(query: str, top_k: int = 3) -> list:
    """Search indexed memories."""
    if not _index.vectors_int8:
        reindex_vault()
    return _index.search(query, top_k)
