import os
import fitz  # PyMuPDF
import logging
import base64
import requests
import json
from util import log_timing
import config

# Setup logger
logger = logging.getLogger("RAG_OCR")

class OCRProcessor:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OCRProcessor, cls).__new__(cls)
        return cls._instance

    @log_timing
    def is_image_based_pdf(self, pdf_path: str, threshold: int = 50) -> bool:
        """
        Check if the first few pages of the PDF have enough text.
        If extracted text chars < threshold, assume it's an image/scanned PDF.
        """
        try:
            doc = fitz.open(pdf_path)
            # Check up to first 3 pages
            pages_to_check = min(3, len(doc))
            total_text_len = 0
            
            for i in range(pages_to_check):
                text = doc[i].get_text()
                total_text_len += len(text.strip())
            
            avg_text_per_page = total_text_len / pages_to_check if pages_to_check > 0 else 0
            logger.info(f"📄 PDF Text Density check: Average {avg_text_per_page:.1f} chars/page for {os.path.basename(pdf_path)}")
            
            # Close the document to avoid lock issues
            doc.close()
            
            return avg_text_per_page < threshold
            
        except Exception as e:
            logger.error(f"Error checking PDF text density: {e}")
            return False

    def _encode_pdf_to_base64(self, file_path):
        """Encodes a local PDF file to a base64 string."""
        try:
            with open(file_path, "rb") as pdf_file:
                encoded_string = base64.b64encode(pdf_file.read()).decode("utf-8")
            return f"data:application/pdf;base64,{encoded_string}"
        except FileNotFoundError:
            logger.error(f"Error: The file '{file_path}' was not found.")
            return None

    @log_timing
    def process_pdf(self, pdf_path: str) -> str:
        """
        Process PDF:
        1. Check if it needs OCR.
        2. If standard text PDF, return None (let pymupdf4llm handle it).
        3. If image-based, call OpenRouter API to convert to Markdown.
        """
        if not config.OCR_ENABLED:
            return None
            
        if not self.is_image_based_pdf(pdf_path):
            logger.info("ℹ️ PDF has sufficient text. Skipping OCR.")
            return None
            
        logger.info(f"🔍 Image-based PDF detected: {os.path.basename(pdf_path)}. Sending to OpenRouter for OCR...")
        
        # 1. Encode the PDF
        pdf_data_url = self._encode_pdf_to_base64(pdf_path)
        if not pdf_data_url:
            return None

        # 2. Get API Key (Prefer safe safe handling, fallback to config if structured differently)
        # Using the key from config.LLM_CONFIGS["openrouter"] since that's where we saw it.
        api_key = config.LLM_CONFIGS.get("openrouter", {}).get("api_key")
        
        if not api_key:
            logger.error("❌ No OpenRouter API key found in config.LLM_CONFIGS['openrouter']. Cannot proceed with OCR.")
            return None

        # 3. Prepare the API Request
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://agentic-rag-local", 
            "X-Title": "Agentic-RAG OCR"
        }

        payload = {
            "model": config.OCR_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Please convert this PDF document into clean, formatted Markdown. Preserve headers, tables, and lists."
                        },
                        {
                            "type": "file",
                            "file": {
                                "type": "pdf",
                                "file_data": pdf_data_url 
                            }
                        }
                    ]
                }
            ],
            "temperature": 0.2, # Low temperature for faithful extraction
            "max_tokens": 12000 # Increase token limit for potentially large outputs
        }

        # 4. Send Request
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload),
                timeout=120 # PDF processing might take time
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    markdown_content = result['choices'][0]['message']['content']
                    logger.info("✅ OCR successful. Markdown generated.")
                    return markdown_content
                else:
                    logger.warning(f"⚠️ Response received but no content generated: {result}")
                    return None
            else:
                logger.error(f"❌ OpenRouter API Error {response.status_code}: {response.text}")
                return None

        except Exception as e:
            logger.error(f"❌ OCR API request failed: {e}")
            return None
