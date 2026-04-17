#!/usr/bin/env python
"""
Setup script to ingest PDF books into the knowledge base
Usage: python setup_knowledge_base.py
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from agents.knowledge_base import get_knowledge_base, print_knowledge_base_stats


def setup_biblical_sources():
    """Ingest biblical reference PDFs"""
    kb = get_knowledge_base()
    
    print("\n" + "="*60)
    print("Setting up Biblical Reference Sources")
    print("="*60)
    
    # Define biblical PDF sources
    # Update these paths to match your actual PDF locations
    pdf_sources = {
        "../knowledge_base/pdfs/kjv_bible.pdf": "King James Version 1611",
        "../knowledge_base/pdfs/matthew_henry_commentary.pdf": "Matthew Henry Commentary",
        "../knowledge_base/pdfs/pulpit_commentary.pdf": "Pulpit Commentary",
    }
    
    ingested_count = 0
    for pdf_path, source_name in pdf_sources.items():
        pdf_full_path = os.path.join(os.path.dirname(__file__), pdf_path)
        if os.path.exists(pdf_full_path):
            try:
                count = kb.ingest_pdf(pdf_full_path, source_name, collection_type="biblical")
                ingested_count += count
            except Exception as e:
                print(f"[ERROR] Failed to ingest {source_name}: {e}")
        else:
            print(f"[INFO] Skipping (not found): {source_name}")
            print(f"       Expected at: {pdf_full_path}")
    
    return ingested_count


def setup_academic_sources():
    """Ingest academic/scholarly PDFs for professor characters"""
    kb = get_knowledge_base()
    
    print("\n" + "="*60)
    print("Setting up Academic Reference Sources")
    print("="*60)
    
    # Define academic PDF sources
    pdf_sources = {
        "../knowledge_base/pdfs/biblical_scholarship.pdf": "Biblical Scholarship Foundations",
        "../knowledge_base/pdfs/historical_context.pdf": "Historical Context of the Bible",
        "../knowledge_base/pdfs/hebrew_greek_study.pdf": "Hebrew and Greek Language Study",
    }
    
    ingested_count = 0
    for pdf_path, source_name in pdf_sources.items():
        pdf_full_path = os.path.join(os.path.dirname(__file__), pdf_path)
        if os.path.exists(pdf_full_path):
            try:
                count = kb.ingest_pdf(pdf_full_path, source_name, collection_type="academic")
                ingested_count += count
            except Exception as e:
                print(f"[ERROR] Failed to ingest {source_name}: {e}")
        else:
            print(f"[INFO] Skipping (not found): {source_name}")
            print(f"       Expected at: {pdf_full_path}")
    
    return ingested_count


def show_usage():
    """Show usage instructions"""
    print("\n" + "="*60)
    print("KNOWLEDGE BASE SETUP - USAGE INSTRUCTIONS")
    print("="*60)
    print("""
To add PDF files to the knowledge base:

1. Create folder structure:
   mkdir -p knowledge_base/pdfs

2. Place your PDF files in the knowledge_base/pdfs/ folder:
   - For biblical characters: kjv_bible.pdf, matthew_henry_commentary.pdf, etc.
   - For professors: biblical_scholarship.pdf, historical_context.pdf, etc.

3. Edit this script (setup_knowledge_base.py) to list your actual PDFs:
   - Update the pdf_sources dictionaries with your file names
   - Add more entries as needed

4. Run the setup:
   python setup_knowledge_base.py

5. The knowledge base will be created in:
   chroma_db/

SUPPORTED PDF SOURCES:
- Biblical texts (KJV, commentaries, study guides)
- Academic works (scholarly analysis, historical context)
- Reference materials (encyclopedias, concordances)
- Theological works (systematic theology, doctrine)

EXAMPLE FOLDER STRUCTURE:
  bible-game-agents/
  ├── knowledge_base/
  │   └── pdfs/
  │       ├── kjv_bible.pdf
  │       ├── matthew_henry_commentary.pdf
  │       ├── biblical_scholarship.pdf
  │       └── historical_context.pdf
  ├── chroma_db/  (created automatically)
  └── src/
      └── agents/
          ├── knowledge_base.py
          └── character_agent.py
""")


def main():
    """Main setup function"""
    print("\n[SETUP] Bible Game - Knowledge Base System")
    print("[SETUP] Initializing ChromaDB and loading embeddings...")
    
    try:
        kb = get_knowledge_base()
        print("[SETUP] ✓ Knowledge base initialized")
        
        # Show current statistics
        print_knowledge_base_stats()
        
        # Attempt to ingest sources
        biblical_count = setup_biblical_sources()
        academic_count = setup_academic_sources()
        
        total_ingested = biblical_count + academic_count
        
        print("\n" + "="*60)
        print("SETUP RESULTS")
        print("="*60)
        print(f"Biblical sources ingested: {biblical_count} chunks")
        print(f"Academic sources ingested: {academic_count} chunks")
        print(f"Total chunks in knowledge base: {total_ingested}")
        
        # Show final statistics
        print_knowledge_base_stats()
        
        if total_ingested == 0:
            print("\n[INFO] No PDF files were found or ingested.")
            show_usage()
        else:
            print("\n[SUCCESS] ✓ Knowledge base is ready!")
            print("         Characters can now cite from these sources.")
        
    except Exception as e:
        print(f"\n[ERROR] Setup failed: {e}")
        import traceback
        traceback.print_exc()
        show_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
