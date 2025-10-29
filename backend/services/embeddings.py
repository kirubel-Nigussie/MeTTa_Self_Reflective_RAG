# from sentence_transformers import SentenceTransformer
# from config import settings

# _model = None

# def get_embedding_model():
#     global _model
#     if _model is None:
#         _model = SentenceTransformer(settings.EMBEDDING_MODEL)
#     return _model

# def embed_texts(texts):
#     """
#     texts: list[str] -> returns list[emb] (lists of floats)
#     """
#     model = get_embedding_model()
#     embs = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
#     return [e.tolist() for e in embs]







# from sentence_transformers import SentenceTransformer
# from config import settings

# _model = None

# def get_embedding_model():
#     """
#     Loads the embedding model once (lazy singleton).
#     """
#     global _model
#     if _model is None:
#         _model = SentenceTransformer(settings.EMBEDDING_MODEL)
#     return _model


# def embed_texts(texts, batch_size: int = 8):
#     """
#     Efficient batch embedding to avoid OOM (Out of Memory) errors.

#     Args:
#         texts (list[str]): List of text chunks.
#         batch_size (int): Number of texts to embed at once.

#     Returns:
#         list[list[float]]: List of embedding vectors.
#     """
#     model = get_embedding_model()
#     embeddings = []

#     # Process texts in smaller batches
#     for i in range(0, len(texts), batch_size):
#         batch = texts[i:i + batch_size]
#         emb = model.encode(batch, convert_to_numpy=True, show_progress_bar=False)
#         embeddings.extend(emb)

#     return [e.tolist() for e in embeddings]












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
