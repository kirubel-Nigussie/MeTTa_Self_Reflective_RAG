

from sentence_transformers import SentenceTransformer
import numpy as np
import gc
from config import settings

_model = None

def get_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model


def embed_texts(texts, batch_size=8):
    """
    Efficiently embed a list of texts in small sub-batches to avoid memory spikes.
    Returns list[list[float]] (embeddings)
    """
    model = get_embedding_model()
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        # Compute embeddings for small batch
        batch_embs = model.encode(batch, convert_to_numpy=True, show_progress_bar=False)
        
        # Convert to lists and store
        all_embeddings.extend(batch_embs.tolist())

        # Explicitly release memory
        del batch, batch_embs
        gc.collect()

    return all_embeddings
