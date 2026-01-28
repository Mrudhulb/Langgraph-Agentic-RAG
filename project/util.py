import os
import config
import pymupdf.layout
import pymupdf4llm
from pathlib import Path
import glob
import time
import logging
from functools import wraps

# Setup logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("RAG_TimeTracker")

def log_timing(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        logger.info(f"Starting {func.__name__}")  # No emoji
        result = func(*args, **kwargs)
        logger.info(f"{func.__name__} completed in {time.time()-start:.2f}s")
        return result
    return wrapper

os.environ["TOKENIZERS_PARALLELISM"] = "false"

def pdf_to_markdown(pdf_path, output_dir):
    # Try OCR first (if enabled and needed)
    try:
        from core.ocr_processor import OCRProcessor
        ocr_result = OCRProcessor().process_pdf(pdf_path)
        
        if ocr_result:
            logger.info(f"✨ Using OCR result for {Path(pdf_path).name}")
            md_cleaned = ocr_result
        else:
            # Fallback to standard extraction
            doc = pymupdf.open(pdf_path)
            md = pymupdf4llm.to_markdown(doc, header=False, footer=False, page_separators=True, ignore_images=True, write_images=False, image_path=None)
            md_cleaned = md.encode('utf-8', errors='surrogatepass').decode('utf-8', errors='ignore')

        output_path = Path(output_dir) / Path(pdf_path).stem
        Path(output_path).with_suffix(".md").write_bytes(md_cleaned.encode('utf-8'))
        
    except Exception as e:
        logger.error(f"Error converting PDF {pdf_path}: {e}")
        # Attempt fallback if OCR failed hard
        if 'doc' not in locals():
            doc = pymupdf.open(pdf_path)
            md = pymupdf4llm.to_markdown(doc, header=False, footer=False, page_separators=True, ignore_images=True, write_images=False, image_path=None)
            md_cleaned = md.encode('utf-8', errors='surrogatepass').decode('utf-8', errors='ignore')
            output_path = Path(output_dir) / Path(pdf_path).stem
            Path(output_path).with_suffix(".md").write_bytes(md_cleaned.encode('utf-8'))

def pdfs_to_markdowns(path_pattern, overwrite: bool = False):
    output_dir = Path(config.MARKDOWN_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    for pdf_path in map(Path, glob.glob(path_pattern)):
        md_path = (output_dir / pdf_path.stem).with_suffix(".md")
        if overwrite or not md_path.exists():
            pdf_to_markdown(pdf_path, output_dir)