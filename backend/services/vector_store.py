
import os
import gc
import chromadb
from config import settings
from services.embeddings import embed_texts

# Use configurable batch size for embeddings
EMBED_BATCH_SIZE = settings.EMBED_BATCH_SIZE

chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_DIR)

collection = chroma_client.get_or_create_collection(
    name="self_reflective_rag_store",
    metadata={"description": "Vector store for PDF document embeddings"}
)

def add_chunks(chunks, batch_size=16):
    """Add chunks to vector store with batching to manage memory."""
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        texts = [c["text"] for c in batch]
        ids = [c["id"] for c in batch]
        metadatas = [c.get("metadata", {}) for c in batch]

        embeddings = embed_texts(texts, batch_size=EMBED_BATCH_SIZE)

        collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

        del batch, texts, embeddings, ids, metadatas
        gc.collect()


def add_pdf_to_chroma(pdf_path, batch_size=16):
    """Stream PDF chunks and embed progressively to avoid memory issues."""
    print(f"📘 Ingesting PDF: {os.path.basename(pdf_path)}")
    batch = []
    count = 0

    # Stream PDF pages and chunks
    for chunk in stream_pdf_chunks(pdf_path):
        batch.append(chunk)
        if len(batch) >= batch_size:
            add_chunks(batch, batch_size=batch_size)
            count += len(batch)
            print(f"  ✅ Inserted {count} chunks so far...")
            batch.clear()
            gc.collect()

    # Process remaining chunks
    if batch:
        add_chunks(batch, batch_size=batch_size)
        count += len(batch)
        print(f"  ✅ Final batch inserted. Total: {count} chunks.")

    gc.collect()
    print(f"🎉 Finished ingesting {os.path.basename(pdf_path)} ({count} chunks).")
    return count


def retrieve_by_text(query, top_k=settings.TOP_K):
    results = collection.query(query_texts=[query], n_results=top_k)
    docs = []
    if results and len(results["ids"]) > 0:
        for i in range(len(results["ids"][0])):
            docs.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            })
    return docs
