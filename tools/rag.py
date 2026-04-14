"""RAG tool — semantic search over company documents (policies, handbooks, SOPs)."""

import logging
from pathlib import Path

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# Module-level vector store instance — initialized once, reused across calls.
_vectorstore = None
_retriever = None


def _init_vectorstore(documents_dir: str, embedding_model: str, chunk_size: int, chunk_overlap: int):
    """Build (or load from cache) a ChromaDB vector store from documents on disk.

    Supports: .txt, .md, .pdf, .docx files in the documents directory.
    """
    global _vectorstore, _retriever

    if _retriever is not None:
        return  # already initialized

    docs_path = Path(documents_dir).resolve()
    if not docs_path.exists():
        docs_path.mkdir(parents=True, exist_ok=True)
        logger.warning("RAG documents directory created (empty): %s", docs_path)
        return

    # Collect document files
    supported_extensions = {".txt", ".md", ".pdf", ".docx"}
    doc_files = [
        f for f in docs_path.rglob("*")
        if f.is_file() and f.suffix.lower() in supported_extensions
    ]

    if not doc_files:
        logger.warning("No documents found in %s — RAG search will return empty results", docs_path)
        return

    # Load documents
    from langchain_community.document_loaders import TextLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    documents = []
    for doc_file in doc_files:
        try:
            if doc_file.suffix.lower() in {".txt", ".md"}:
                loader = TextLoader(str(doc_file), encoding="utf-8")
            else:
                # For PDF/DOCX, try UnstructuredFileLoader
                from langchain_community.document_loaders import UnstructuredFileLoader
                loader = UnstructuredFileLoader(str(doc_file))
            loaded = loader.load()
            # Add source metadata
            for doc in loaded:
                doc.metadata["source"] = doc_file.name
                doc.metadata["path"] = str(doc_file.relative_to(docs_path))
            documents.extend(loaded)
            logger.info("RAG: loaded %s (%d chunks)", doc_file.name, len(loaded))
        except Exception as exc:
            logger.warning("RAG: failed to load %s: %s", doc_file.name, exc)

    if not documents:
        logger.warning("RAG: no documents successfully loaded")
        return

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = splitter.split_documents(documents)
    logger.info("RAG: %d documents → %d chunks", len(documents), len(chunks))

    # Create embeddings + vector store
    from langchain_openai import OpenAIEmbeddings
    from langchain_chroma import Chroma

    embeddings = OpenAIEmbeddings(model=embedding_model)

    # Persist to disk so subsequent startups are fast
    persist_dir = str(docs_path.parent / ".chroma_cache")
    _vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir,
    )
    _retriever = _vectorstore.as_retriever(search_kwargs={"k": 5})
    logger.info("RAG: vector store initialized (%d chunks, persist=%s)", len(chunks), persist_dir)


@tool
def search_company_docs(query: str, top_k: int = 5) -> str:
    """Search company documents (policies, handbooks, SOPs) using semantic search.

    Returns relevant document excerpts with source file attribution.
    Use this to answer questions about company policies, leave rules, HR procedures,
    compliance requirements, or any internal documentation.

    Args:
        query: The search query — what you want to find in company documents.
        top_k: Number of results to return (default 5).
    """
    if _retriever is None:
        return (
            "RAG search is not available. Either no documents have been loaded "
            "in data/policies/, or the RAG system has not been initialized. "
            "Ask the user to add policy documents to the data/policies/ directory."
        )

    try:
        results = _retriever.invoke(query)
        if not results:
            return f"No relevant documents found for: '{query}'"

        # Limit to top_k
        results = results[:top_k]

        output_parts = [f"## Search Results for: '{query}'\n"]
        for i, doc in enumerate(results, 1):
            source = doc.metadata.get("source", "unknown")
            path = doc.metadata.get("path", source)
            content = doc.page_content.strip()
            # Truncate very long chunks
            if len(content) > 800:
                content = content[:800] + "..."
            output_parts.append(
                f"### Result {i} — `{path}`\n{content}\n"
            )

        return "\n".join(output_parts)
    except Exception as exc:
        logger.exception("RAG search failed")
        return f"RAG search error: {exc}"


def get_rag_tools(config) -> list:
    """Initialize the RAG system and return the search tool.

    Called by load_tools.py when rag.enabled is True in config.
    """
    try:
        _init_vectorstore(
            documents_dir=config.rag.documents_dir,
            embedding_model=config.rag.embedding_model,
            chunk_size=config.rag.chunk_size,
            chunk_overlap=config.rag.chunk_overlap,
        )
    except Exception as exc:
        logger.warning("RAG initialization failed: %s", exc)

    return [search_company_docs]
