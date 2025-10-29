# import os
# import chromadb
# from chromadb.config import Settings as ChromaSettings
# from config import settings
# from services.embeddings import embed_texts

# os.makedirs(settings.CHROMA_DB_DIR, exist_ok=True)
# chroma_client = chromadb.Client(ChromaSettings(chroma_db_impl="duckdb+parquet", persist_directory=settings.CHROMA_DB_DIR))
# COLLECTION_NAME = "sr_rag_docs"

# if COLLECTION_NAME in [c.name for c in chroma_client.list_collections()]:
#     collection = chroma_client.get_collection(COLLECTION_NAME)
# else:
#     collection = chroma_client.create_collection(COLLECTION_NAME)

# def add_chunks(chunks):
#     """
#     chunks: list of dicts {id, text, metadata}
#     """
#     ids = [c["id"] for c in chunks]
#     texts = [c["text"] for c in chunks]
#     metadatas = [c.get("metadata", {}) for c in chunks]
#     embeddings = embed_texts(texts)
#     collection.add(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)
#     chroma_client.persist()

# def query_by_embedding(embedding, top_k=5):
#     res = collection.query(query_embeddings=[embedding], n_results=top_k, include=["documents","metadatas","ids","distances"])
#     out = []
#     if res and res.get("documents"):
#         docs = res["documents"][0]
#         ids = res.get("ids",[[]])[0]
#         metas = res.get("metadatas",[[]])[0]
#         dists = res.get("distances",[[]])[0]
#         for i, txt in enumerate(docs):
#             score = 1.0 - dists[i] if dists else 1.0
#             out.append({"id": ids[i], "text": txt, "metadata": metas[i] if metas else {}, "score": float(score)})
#     return out

# def retrieve_by_text(query_text, top_k=5):
#     emb = embed_texts([query_text])[0]
#     return query_by_embedding(emb, top_k=top_k)













# import chromadb
# from chromadb.config import Settings
# from config import settings

# # ✅ New ChromaDB API (v1.1+)
# chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_DIR)

# # Create or get your collection (you can name it anything)
# collection = chroma_client.get_or_create_collection(name="documents")

# def add_chunks(chunks):
#     """Add document chunks to the Chroma vector store."""
#     ids = [str(i) for i, _ in enumerate(chunks)]
#     texts = [c["text"] for c in chunks]
#     metas = [{"id": c["id"]} for c in chunks]
#     collection.add(documents=texts, ids=ids, metadatas=metas)

# def retrieve_by_text(query, top_k=5):
#     """Retrieve most similar chunks."""
#     results = collection.query(query_texts=[query], n_results=top_k)
#     docs = []
#     for ids, metas, texts in zip(results["ids"][0], results["metadatas"][0], results["documents"][0]):
#         docs.append({"id": metas["id"], "text": texts})
#     return docs




















# import os
# import gc
# import chromadb
# from chromadb.config import Settings
# from config import settings
# from services.embeddings import embed_texts
# from services.pdf_loader import stream_pdf_chunks

# # Initialize Chroma client (new configuration style)
# chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_DIR)

# # Create or get collection
# collection = chroma_client.get_or_create_collection(
#     name="self_reflective_rag_store",
#     metadata={"description": "Vector store for PDF document embeddings"}
# )


# def add_chunks(chunks, batch_size=16):
#     """
#     Add text chunks to Chroma in small batches to prevent memory overload.
#     """
#     for i in range(0, len(chunks), batch_size):
#         batch = chunks[i:i + batch_size]
#         texts = [c["text"] for c in batch]
#         ids = [c["id"] for c in batch]
#         metadatas = [c["metadata"] for c in batch]

#         # Embed in smaller sub-batches (handled inside embed_texts)
#         embeddings = embed_texts(texts)

#         # Insert into Chroma
#         collection.add(
#             ids=ids,
#             documents=texts,
#             embeddings=embeddings,
#             metadatas=metadatas
#         )

#         # Free memory explicitly
#         del batch, texts, embeddings, ids, metadatas
#         gc.collect()


# def add_pdf_to_chroma(pdf_path, batch_size=16):
#     """
#     Stream a PDF file page-by-page, embed and insert chunks incrementally.
#     Prevents full-memory load.
#     """
#     print(f"📘 Ingesting PDF: {os.path.basename(pdf_path)}")
#     batch = []
#     count = 0

#     for chunk in stream_pdf_chunks(pdf_path):
#         batch.append(chunk)
#         if len(batch) >= batch_size:
#             add_chunks(batch, batch_size=batch_size)
#             count += len(batch)
#             print(f"  ✅ Inserted {count} chunks so far...")
#             batch.clear()
#             gc.collect()

#     # process remaining
#     if batch:
#         add_chunks(batch, batch_size=batch_size)
#         count += len(batch)
#         print(f"  ✅ Final batch inserted. Total: {count} chunks.")

#     gc.collect()
#     print(f"🎉 Finished ingesting {os.path.basename(pdf_path)} ({count} chunks).")


# def retrieve_by_text(query, top_k=settings.TOP_K):
#     """
#     Retrieve the most relevant chunks for a given query using similarity search.
#     """
#     results = collection.query(
#         query_texts=[query],
#         n_results=top_k
#     )

#     docs = []
#     if results and len(results["ids"]) > 0:
#         for i in range(len(results["ids"][0])):
#             docs.append({
#                 "id": results["ids"][0][i],
#                 "text": results["documents"][0][i],
#                 "metadata": results["metadatas"][0][i],
#                 "distance": results["distances"][0][i]
#             })
#     return docs


# def clear_chroma():
#     """
#     Utility to clear the vector database (for dev/test use).
#     """
#     chroma_client.delete_collection("self_reflective_rag_store")
#     print("🧹 Cleared Chroma vector store.")


# if __name__ == "__main__":
#     # Simple test (you can comment this out later)
#     test_pdf = "./data/uploads/test.pdf"
#     if os.path.exists(test_pdf):
#         add_pdf_to_chroma(test_pdf, batch_size=8)
#         res = retrieve_by_text("What is discussed in the document?", top_k=3)
#         print(res)
#     else:
#         print("⚠️ No test PDF found. Upload one via /upload_pdf endpoint.")










# import os
# import gc
# import chromadb
# from config import settings
# from services.embeddings import embed_texts
# from services.pdf_loader import stream_pdf_chunks

# # Initialize Chroma client
# chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_DIR)

# # Create or get collection
# collection = chroma_client.get_or_create_collection(
#     name="self_reflective_rag_store",
#     metadata={"description": "Vector store for PDF document embeddings"}
# )


# def add_chunks(chunks, batch_size=16):
#     """
#     Add text chunks to Chroma in small batches to prevent memory overload.
#     """
#     for i in range(0, len(chunks), batch_size):
#         batch = chunks[i:i + batch_size]
#         texts = [c["text"] for c in batch]
#         ids = [c["id"] for c in batch]
#         metadatas = [c["metadata"] for c in batch]

#         # Embed with internal batching and memory cleanup
#         embeddings = embed_texts(texts, batch_size=EMBED_BATCH_SIZE)

#         collection.add(
#             ids=ids,
#             documents=texts,
#             embeddings=embeddings,
#             metadatas=metadatas
#         )

#         # Free memory immediately
#         del batch, texts, embeddings, ids, metadatas
#         gc.collect()

#         print(f"✅ Added batch {i // batch_size + 1}/{(len(chunks) + batch_size - 1) // batch_size}")


# def add_pdf_to_chroma(pdf_path, batch_size=16):
#     """
#     Stream a PDF file page-by-page, embed and insert chunks incrementally.
#     Prevents full-memory load.
#     """
#     print(f"📘 Ingesting PDF: {os.path.basename(pdf_path)}")
#     batch = []
#     count = 0

#     for chunk in stream_pdf_chunks(pdf_path):
#         batch.append(chunk)
#         if len(batch) >= batch_size:
#             add_chunks(batch, batch_size=batch_size)
#             count += len(batch)
#             print(f"  ✅ Inserted {count} chunks so far...")
#             batch.clear()
#             gc.collect()

#     if batch:
#         add_chunks(batch, batch_size=batch_size)
#         count += len(batch)
#         print(f"  ✅ Final batch inserted. Total: {count} chunks.")

#     gc.collect()
#     print(f"🎉 Finished ingesting {os.path.basename(pdf_path)} ({count} chunks).")


# def retrieve_by_text(query, top_k=settings.TOP_K):
#     """
#     Retrieve the most relevant chunks for a given query using similarity search.
#     """
#     results = collection.query(query_texts=[query], n_results=top_k)

#     docs = []
#     if results and len(results["ids"]) > 0:
#         for i in range(len(results["ids"][0])):
#             docs.append({
#                 "id": results["ids"][0][i],
#                 "text": results["documents"][0][i],
#                 "metadata": results["metadatas"][0][i],
#                 "distance": results["distances"][0][i]
#             })
#     return docs


# def clear_chroma():
#     chroma_client.delete_collection("self_reflective_rag_store")
#     print("🧹 Cleared Chroma vector store.")


# if __name__ == "__main__":
#     test_pdf = "./data/uploads/test.pdf"
#     if os.path.exists(test_pdf):
#         add_pdf_to_chroma(test_pdf, batch_size=8)
#         res = retrieve_by_text("What is discussed in the document?", top_k=3)
#         print(res)
#     else:
#         print("⚠️ No test PDF found. Upload one via /upload_pdf endpoint.")















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
