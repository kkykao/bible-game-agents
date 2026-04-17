"""
Knowledge Base Management System
Manages PDF ingestion and semantic search for character knowledge
Uses ChromaDB for local vector storage (no cloud dependencies)
"""
import os
import json
from typing import List, Tuple, Dict
from pathlib import Path
import PyPDF2
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings


class PDFKnowledgeBase:
    """Manages PDF knowledge base with semantic search capabilities"""
    
    def __init__(self, pdf_dir: str = "../knowledge_base/pdfs", 
                 chroma_dir: str = "../chroma_db"):
        """Initialize knowledge base with ChromaDB (local vector DB)"""
        self.pdf_dir = Path(pdf_dir)
        self.chroma_dir = Path(chroma_dir)
        self.pdf_dir.mkdir(parents=True, exist_ok=True)
        self.chroma_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"[KB] Initializing ChromaDB at {self.chroma_dir}", flush=True)
        
        # Use ChromaDB - simple, local, no API keys needed
        self.chroma_client = chromadb.Client(
            Settings(
                chroma_db_impl="duckdb",
                persist_directory=str(self.chroma_dir),
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding model (local, no API calls)
        print("[KB] Loading embedding model (all-MiniLM-L6-v2)...", flush=True)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Create collections for different character types
        self.biblical_collection = self.chroma_client.get_or_create_collection(
            name="biblical_sources",
            metadata={"description": "Sacred texts and biblical commentaries"}
        )
        self.academic_collection = self.chroma_client.get_or_create_collection(
            name="academic_sources",
            metadata={"description": "Academic biblical scholarship"}
        )
        
        print("[KB] ✓ Knowledge base initialized", flush=True)
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Tuple[str, int]]:
        """Extract text from PDF with page numbers"""
        passages = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        text = page.extract_text()
                        if text and text.strip():
                            # Split into chunks (paragraphs or sentences)
                            chunks = self._chunk_text(text)
                            for chunk in chunks:
                                passages.append((chunk, page_num))
                    except Exception as e:
                        print(f"[KB] Warning: Failed to extract page {page_num}: {e}", flush=True)
                        continue
        except Exception as e:
            print(f"[KB] Error reading PDF {pdf_path}: {e}", flush=True)
            return []
        
        return passages
    
    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """Split text into manageable chunks"""
        # Clean text
        text = text.replace('\n', ' ').strip()
        
        # Split by sentences (period followed by space and capital letter)
        import re
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_chunk) + len(sentence) + 1 < chunk_size:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return [c for c in chunks if len(c) > 50]  # Filter out tiny chunks
    
    def ingest_pdf(self, pdf_path: str, source_name: str, 
                   collection_type: str = "biblical") -> int:
        """Ingest a PDF into the knowledge base"""
        pdf_path = str(pdf_path)
        
        if not os.path.exists(pdf_path):
            print(f"[KB] Error: File not found: {pdf_path}", flush=True)
            return 0
        
        print(f"[KB] Ingesting '{source_name}' from {pdf_path}...", flush=True)
        
        passages = self.extract_text_from_pdf(pdf_path)
        if not passages:
            print(f"[KB] Warning: No text extracted from {pdf_path}", flush=True)
            return 0
        
        collection = (self.biblical_collection if collection_type == "biblical" 
                     else self.academic_collection)
        
        # Add to vector DB with metadata
        doc_ids = []
        for i, (text, page_num) in enumerate(passages):
            doc_id = f"{source_name.replace(' ', '_')}_p{page_num}_{i}"
            doc_ids.append(doc_id)
            
            try:
                collection.add(
                    ids=[doc_id],
                    documents=[text],
                    metadatas=[{
                        "source": source_name,
                        "page": page_num,
                        "chunk": i
                    }]
                )
            except Exception as e:
                print(f"[KB] Error adding document {doc_id}: {e}", flush=True)
        
        print(f"[KB] ✓ Ingested {len(doc_ids)} chunks from '{source_name}'", flush=True)
        return len(doc_ids)
    
    def search_knowledge(self, query: str, collection_type: str = "biblical",
                        n_results: int = 3) -> List[Dict]:
        """Search for relevant passages using semantic similarity"""
        try:
            collection = (self.biblical_collection if collection_type == "biblical"
                         else self.academic_collection)
            
            results = collection.query(
                query_texts=[query],
                n_results=min(n_results, 5)  # Cap at 5 to be safe
            )
            
            # Format results with citations
            formatted = []
            if results.get('documents') and results['documents'][0]:
                for doc, metadata, distance in zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results.get('distances', [[0]*n_results])[0]
                ):
                    # Only include results with reasonable similarity
                    if distance < 1.0:  # Lower distance = better match
                        formatted.append({
                            'text': doc[:250],  # Truncate for readability
                            'source': metadata['source'],
                            'page': metadata['page'],
                            'citation': f"{metadata['source']} (p. {metadata['page']})",
                            'distance': distance
                        })
            
            return formatted
        except Exception as e:
            print(f"[KB] Error searching knowledge base: {e}", flush=True)
            return []
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the knowledge base"""
        biblical_count = self.biblical_collection.count()
        academic_count = self.academic_collection.count()
        
        return {
            'biblical_chunks': biblical_count,
            'academic_chunks': academic_count,
            'total_chunks': biblical_count + academic_count
        }


# Global instance
_knowledge_base = None

def get_knowledge_base():
    """Get or create knowledge base instance"""
    global _knowledge_base
    if not _knowledge_base:
        _knowledge_base = PDFKnowledgeBase()
    return _knowledge_base

def print_knowledge_base_stats():
    """Print knowledge base statistics"""
    kb = get_knowledge_base()
    stats = kb.get_collection_stats()
    print(f"\n[KB] Knowledge Base Statistics:")
    print(f"  - Biblical texts: {stats['biblical_chunks']} chunks")
    print(f"  - Academic texts: {stats['academic_chunks']} chunks")
    print(f"  - Total: {stats['total_chunks']} chunks\n")
