from app.rag.loader import PDFLoader
from app.rag.splitter import TextSplitter
from app.rag.vectorstore import VectorStoreManager
from typing import List, Optional
from app.services.llm_service import LLMService
from app.core.config import settings
from langchain_core.documents import Document
from utils.helpers import safe_load_json, pil_image_to_base64
from utils.prompts import VISUAL_ANALYST_PROMPT

class IngestService:
    def __init__(self):
        self.loader = PDFLoader()
        self.splitter = TextSplitter()
        self.vectorstore = VectorStoreManager()
        self.llm_service = LLMService()

    def process_pdf_simple(self, file_path: str) -> List[str]:
        print(f"Loading PDF from {file_path}")
        docs = self.loader.load(file_path)
        print(f"Loaded {len(docs)} pages from PDF")
        
        # Simple TOC extraction: first line of first 10 pages
        toc = []
        for doc in docs[:10]:
            lines = doc.page_content.strip().split('\n')
            if lines:
                toc.append(lines[0])
        print(f"Extracted TOC: {toc}")
        chunks = self.splitter.split(docs)
        print(f"Split documents into {len(chunks)} chunks")

        # Normalize chunks to ensure each vector store point follows the same schema:
        # - page_content: a short summary for embedding
        # - metadata: { source, page, full_content, details_length, raw_parsed }
        normalized_chunks: List[Document] = []
        for c in chunks:
            # derive a short summary (first line or first 200 chars)
            text = c.page_content or ""
            first_line = text.strip().split('\n', 1)[0] if text.strip() else ""
            summary = first_line if first_line else (text[:200].strip())

            metadata = {}
            try:
                # preserve any existing metadata on chunk
                metadata = dict(c.metadata) if getattr(c, 'metadata', None) else {}
            except Exception:
                metadata = {}

            metadata.update({
                "source": file_path,
                "page": metadata.get("page"),
            })

            full_content = f"""Summary: {summary}\nDescription: {text}"""
            metadata.update({
                "full_content": full_content,
                "details_length": len(full_content),
                "raw_parsed": False,
            })

            normalized_chunks.append(Document(page_content=summary, metadata=metadata))

        self.vectorstore.add_documents(normalized_chunks)
        print(f"Added {len(normalized_chunks)} chunks to vector store")
        
        return list(set(toc))

    def process_pdf_visual(self, file_path: str) -> List[str]:

        try:
            from pdf2image import convert_from_path
        except Exception as e:
            print("pdf2image not available or failed to import; falling back to text-only processing.")
            return self.process_pdf_simple(file_path)

        try:
            print(f"Rendering PDF pages to images for visual processing: {file_path}")
            pil_images = convert_from_path(file_path)
            print(f"Converted {len(pil_images)} pages to images")
        except Exception as e:
            print(f"Failed to render PDF to images: {e}; falling back to text-only processing.")
            return self.process_pdf_simple(file_path)

        try:
            text_pages = self.loader.load(file_path)
        except Exception:
            text_pages = []

        descriptions: List[str] = []
        documents_to_add: List[Document] = []

        for idx, img in enumerate(pil_images, start=1):
            try:

                # Convert PIL image to base64 using helper
                img_b64 = pil_image_to_base64(img)

                print(f"Sending page {idx} to VLM for analysis using LLMService")
                content = self.llm_service.predict_messages(prompt=VISUAL_ANALYST_PROMPT, base_64_image=img_b64)

                if content is None:
                    print(f"LLM returned no content for page {idx}; using text fallback snippet.")
                    content = ""

                descriptions.append(content)

                # Build metadata and prefer the parsed 'summary' for embeddings
                metadata = {"source": file_path, "page": idx, "type": "visual"}
                page_text_snippet = text_pages[idx - 1].page_content[:300] if idx - 1 < len(text_pages) else ""
                metadata["text_snippet"] = page_text_snippet

                parsed = safe_load_json(content)
                if parsed:
                    summary = (parsed.get("summary") or "").strip()
                    details = parsed.get("details", "") or ""

                    full_content = f"""Summary: {summary}\nDescription: {details}"""
                    metadata.update({
                        "full_content": full_content,
                        "details_length": len(full_content),
                        "raw_parsed": True,
                    })

                    # page_content should be the summary for embedding; fall back to details or content
                    page_content = summary or (details[:2000] if isinstance(details, str) else (content or "")[:2000])
                    doc = Document(page_content=page_content, metadata=metadata)
                else:
                    # Not valid JSON — store raw content and mark as unparsed
                    store_text = content if content else page_text_snippet
                    # attempt a short summary from available text
                    s = store_text.strip().split('\n', 1)[0] if store_text else ""
                    full_content = f"""Summary: {s}\nDescription: {store_text}"""
                    metadata.update({
                        "full_content": full_content,
                        "details_length": len(full_content),
                        "raw_parsed": False,
                    })
                    page_content = s or store_text[:200]
                    doc = Document(page_content=page_content, metadata=metadata)

                documents_to_add.append(doc)

            except Exception as e:
                # Per-page failure should not abort the whole process. Log and continue.
                print(f"Error processing page {idx} visually: {e}; using text-only fallback for this page.")
                fallback_snippet = text_pages[idx - 1].page_content[:1000] if idx - 1 < len(text_pages) else ""
                summary = fallback_snippet.strip().split('\n', 1)[0] if fallback_snippet else ""
                full_content = f"""Summary: {summary}\nDescription: {fallback_snippet}"""
                metadata = {"source": file_path, "page": idx, "type": "visual", "raw_parsed": False}
                metadata.update({"full_content": full_content, "details_length": len(full_content)})
                page_content = summary or fallback_snippet[:200]
                doc = Document(page_content=page_content, metadata=metadata)
                descriptions.append(fallback_snippet)
                documents_to_add.append(doc)

        if documents_to_add:
            try:
                print(f"Adding {len(documents_to_add)} visual description documents to vector store")
                self.vectorstore.add_documents(documents_to_add)
            except Exception as e:
                print(f"Failed to add visual documents to vector store: {e}; falling back to text pipeline.")
                return self.process_pdf_simple(file_path)

        return descriptions
