from pathlib import Path
import shutil
import config
from util import pdfs_to_markdowns, pdf_to_markdown, docx_to_markdown, log_timing

class DocumentManager:

    def __init__(self, rag_system):
        self.rag_system = rag_system
        self.markdown_dir = Path(config.MARKDOWN_DIR)
        self.markdown_dir.mkdir(parents=True, exist_ok=True)
        
    @log_timing    
    def add_documents(self, document_paths, progress_callback=None):
        if not document_paths:
            return 0, 0
            
        document_paths = [document_paths] if isinstance(document_paths, str) else document_paths
        allowed_extensions = [".pdf", ".md", ".doc", ".docx"]
        document_paths = [p for p in document_paths if p and Path(p).suffix.lower() in allowed_extensions]
        
        if not document_paths:
            return 0, 0

            
        added = 0
        skipped = 0
            
        for i, doc_path in enumerate(document_paths):
            if progress_callback:
                progress_callback((i + 1) / len(document_paths), f"Processing {Path(doc_path).name}")
                
            doc_name = Path(doc_path).stem
            md_path = self.markdown_dir / f"{doc_name}.md"
            
            if md_path.exists():
                skipped += 1
                continue
                
            try:            
                ext = Path(doc_path).suffix.lower()
                if ext == ".md":
                    shutil.copy(doc_path, md_path)
                elif ext in [".doc", ".docx"]:
                    docx_to_markdown(str(doc_path), self.markdown_dir)
                else:
                    pdf_to_markdown(str(doc_path), self.markdown_dir)
                parent_chunks, child_chunks = self.rag_system.chunker.create_chunks_single(md_path)
                
                if not child_chunks:
                    skipped += 1
                    continue
                
                collection = self.rag_system.vector_db.get_collection(self.rag_system.collection_name)
                collection.add_documents(child_chunks)
                self.rag_system.parent_store.save_many(parent_chunks)
                
                added += 1
                
            except Exception as e:
                import traceback
                print(f"Error processing {doc_path}: {e}")
                traceback.print_exc()
                skipped += 1
            
        return added, skipped
    
    def get_markdown_files(self):
        if not self.markdown_dir.exists():
            return []
        return sorted([p.name.replace(".md", ".pdf") for p in self.markdown_dir.glob("*.md")])
    
    def clear_all(self):
        if self.markdown_dir.exists():
            shutil.rmtree(self.markdown_dir)
            self.markdown_dir.mkdir(parents=True, exist_ok=True)
        
        self.rag_system.parent_store.clear_store()
        self.rag_system.vector_db.delete_collection(self.rag_system.collection_name)
        self.rag_system.vector_db.create_collection(self.rag_system.collection_name)