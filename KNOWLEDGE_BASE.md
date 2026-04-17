# Knowledge Base System Documentation

## Overview

The Bible Game now features an advanced **Knowledge Base System** that uses **Retrieval Augmented Generation (RAG)** to enhance character responses with citations from actual PDF sources.

### What This Does

- ✅ Characters cite from your PDF books and reference materials
- ✅ Responses include page numbers and source attribution
- ✅ No external APIs needed for search (local ChromaDB)
- ✅ Automatic semantic matching of user questions to relevant passages
- ✅ Different sources for biblical characters vs. academic/professor characters

## Architecture

```
User Question
    ↓
[Semantic Search] Find relevant PDF passages using embeddings
    ↓
[Context Injection] Add top 3 matching passages to system prompt
    ↓
[Claude API] Generate response using injected context
    ↓
User Response (with PDF citations and page numbers)
```

## System Components

### 1. **knowledge_base.py** - Core Knowledge Base Module
- Manages PDF ingestion and storage
- Performs semantic similarity searches
- Uses ChromaDB for local vector database
- Uses SentenceTransformers for embeddings (all local, no API calls)

### 2. **character_agent.py** - Enhanced Character Agent
- Integrated with knowledge base
- Automatically retrieves relevant passages
- Injects knowledge as context in system prompts
- Tracks and displays source citations

### 3. **setup_knowledge_base.py** - PDF Ingestion Script
- Extracts text from PDFs
- Chunks text into manageable segments
- Generates embeddings automatically
- Stores in ChromaDB database

## How to Set Up

### Step 1: Install Dependencies

The required packages are already in `requirements.txt`:
- `PyPDF2` - PDF text extraction
- `sentence-transformers` - Semantic embeddings
- `chromadb` - Vector database

They were installed when you ran: `pip install -r requirements-fixed.txt`

### Step 2: Prepare Your PDF Files

Create the `knowledge_base/pdfs/` directory (already created):

```
bible-game-agents/
└── knowledge_base/
    └── pdfs/
        ├── kjv_bible.pdf
        ├── matthew_henry_commentary.pdf
        ├── biblical_scholarship.pdf
        └── historical_context.pdf
```

### Step 3: Update the Setup Script

Edit `src/setup_knowledge_base.py` and update the PDF file paths:

```python
# For biblical characters
pdf_sources = {
    "../knowledge_base/pdfs/kjv_bible.pdf": "King James Version 1611",
    "../knowledge_base/pdfs/matthew_henry_commentary.pdf": "Matthew Henry Commentary",
    # Add your PDFs here
}

# For professor characters
pdf_sources = {
    "../knowledge_base/pdfs/biblical_scholarship.pdf": "Biblical Scholarship",
    "../knowledge_base/pdfs/historical_context.pdf": "Historical Context",
    # Add your PDFs here
}
```

### Step 4: Run the Ingestion Script

```bash
cd src
python setup_knowledge_base.py
```

This will:
1. Extract text from all PDFs
2. Create semantic embeddings
3. Store in ChromaDB database
4. Show statistics of ingested content

**Output Example:**
```
[SETUP] Bible Game - Knowledge Base System
[KB] Ingesting 'King James Version 1611'...
[KB] ✓ Ingested 5,342 chunks from 'King James Version 1611'
[KB] Ingesting 'Matthew Henry Commentary'...
[KB] ✓ Ingested 3,214 chunks from 'Matthew Henry Commentary'

[KB] Knowledge Base Statistics:
  - Biblical texts: 8,556 chunks
  - Academic texts: 0 chunks
  - Total: 8,556 chunks
```

### Step 5: Restart the Backend

```bash
cd src
python main.py
```

The backend will now automatically use the knowledge base!

## How It Works

### During Character Response Generation

1. **User asks a question**: "What did Moses say about the Ten Commandments?"

2. **Knowledge Base Search**: 
   - Converts question to semantic embedding
   - Searches biblical sources for similar passages
   - Retrieves top 3 results with highest similarity

3. **Context Injection**:
   - Retrieved passages are added to system prompt
   - Claude can cite these passages directly
   - Includes page numbers and source information

4. **Response Generation**:
   - Claude generates response using injected knowledge
   - Automatically includes citations
   - Response includes page references

5. **Final Output**:
   ```
   And God spake all these words, saying, I am the LORD thy God...
   - King James Version 1611 (p. 15)
   
   These commandments were inscribed upon the Mount of Sinai...
   - Matthew Henry Commentary (p. 432)
   ```

## Supported PDF Types

### Biblical Sources ✅
- King James Version Bible
- Commentaries (Matthew Henry, Pulpit, etc.)
- Study guides and references
- Theological works
- Biblical encyclopedias

### Academic Sources ✅
- Biblical scholarship papers
- Historical analysis works
- Language study materials (Hebrew, Greek)
- Systematic theology
- Archaeological findings

## Advanced: Customizing Knowledge Base

### Add More PDFs Dynamically

```python
from agents.knowledge_base import get_knowledge_base

kb = get_knowledge_base()

# Add a PDF to biblical sources
kb.ingest_pdf(
    pdf_path="path/to/your_book.pdf",
    source_name="Book Title",
    collection_type="biblical"
)

# Add a PDF to academic sources
kb.ingest_pdf(
    pdf_path="path/to/scholarly_work.pdf",
    source_name="Work Title",
    collection_type="academic"
)
```

### Search the Knowledge Base Directly

```python
from agents.knowledge_base import get_knowledge_base

kb = get_knowledge_base()

# Search biblical sources
results = kb.search_knowledge(
    query="What is faith?",
    collection_type="biblical",
    n_results=5
)

for result in results:
    print(f"{result['citation']}")
    print(f"  {result['text']}")
```

### View Knowledge Base Statistics

```python
from agents.knowledge_base import print_knowledge_base_stats

print_knowledge_base_stats()
```

## Configuration Options

### Chunk Size
In `knowledge_base.py`, adjust the chunk size (default 500 characters):

```python
def _chunk_text(self, text: str, chunk_size: int = 500):
    # Larger = fewer chunks, faster search but less granular
    # Smaller = more chunks, slower search but more precise
```

### Number of Retrieved Results
In `character_agent.py`, adjust how many passages to retrieve:

```python
knowledge_results = kb.search_knowledge(
    query=player_message,
    collection_type=collection_type,
    n_results=5  # Change from 3 to 5 for more context
)
```

### Similarity Threshold
In `knowledge_base.py`, adjust the minimum match quality:

```python
if distance < 1.0:  # Lower values = stricter matching
    # Include in results
```

## Performance Considerations

### Storage
- Embeddings stored in `chroma_db/` directory
- ~10MB per 100 PDFs (encrypted and compressed)
- No external cloud storage needed

### Speed
- First search: 2-3 seconds (loads model)
- Subsequent searches: 0.5-1 second
- No network latency (all local)

### Memory
- Embedding model: ~400MB
- ChromaDB cache: ~100MB
- Total overhead: ~500MB

## Troubleshooting

### "PDF file not found"
- Check the file path in `setup_knowledge_base.py`
- Ensure PDF is in `knowledge_base/pdfs/` directory
- Use forward slashes `/` in paths

### "No embeddings generated"
- Verify PyPDF2 is installed: `pip show PyPDF2`
- Check PDF is not scanned image (requires OCR)
- Ensure PDF has extractable text

### "ChromaDB database is locked"
- Kill any existing Python processes
- Delete `chroma_db/` directory
- Re-run: `python setup_knowledge_base.py`

### Characters not citing sources
- Check that PDFs were ingested successfully
- Look at setup script output for chunk counts
- Verify ChromaDB has data: `kb.get_collection_stats()`

## Example Workflow

### Complete Setup Example

```bash
# 1. Place PDFs in the folder
cp ~/Downloads/kjv_bible.pdf knowledge_base/pdfs/
cp ~/Downloads/commentary.pdf knowledge_base/pdfs/

# 2. Edit src/setup_knowledge_base.py
# Update the pdf_sources dictionary with your files

# 3. Run setup
cd src
python setup_knowledge_base.py

# 4. Restart backend
python main.py

# 5. Test in browser
# Ask biblical character: "What did the Lord say about love?"
# You should see citations from your PDFs!
```

## Next Steps

1. **Add Your Books**: Place PDF files in `knowledge_base/pdfs/`
2. **Run Setup**: Execute `python setup_knowledge_base.py`
3. **Test**: Ask characters questions and verify they cite sources
4. **Expand**: Keep adding more PDFs as needed

## Technical Details

### How Semantic Search Works

1. **Question Embedding**: User question converted to 384-dimensional vector
2. **Passage Embeddings**: All PDF passages pre-converted to vectors
3. **Similarity Calculation**: Compute distance between question and passages
4. **Top-K Retrieval**: Return 3 closest passages
5. **Context Injection**: Add matching passages to Claude system prompt

### Why Local Processing?

- ✅ **Privacy**: Your PDFs never leave your computer
- ✅ **Speed**: No network latency
- ✅ **Cost**: No API charges for embeddings
- ✅ **Reliability**: Doesn't depend on external services
- ✅ **Offline**: Can work without internet

## API Reference

### PDFKnowledgeBase Class

```python
class PDFKnowledgeBase:
    def __init__(pdf_dir, chroma_dir)
    def extract_text_from_pdf(pdf_path) -> List[Tuple[str, int]]
    def ingest_pdf(pdf_path, source_name, collection_type) -> int
    def search_knowledge(query, collection_type, n_results) -> List[Dict]
    def get_collection_stats() -> Dict
```

### get_knowledge_base()
Returns singleton instance of knowledge base

### print_knowledge_base_stats()
Prints current statistics about ingested content

## Future Enhancements

Potential improvements:
- [ ] Support for scanned PDFs with OCR
- [ ] Automatic bibliographic metadata extraction
- [ ] Web UI for managing knowledge base
- [ ] Hybrid search (semantic + keyword)
- [ ] Citation quality scoring
- [ ] Multi-language support

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Verify all files are in correct locations
3. Check Python version compatibility (3.8+)
4. Review setup_knowledge_base.py output for errors
