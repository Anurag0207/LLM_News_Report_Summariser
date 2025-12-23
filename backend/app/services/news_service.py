"""News and text processing service."""
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import re


class NewsService:
    """Service for processing news articles and text."""
    
    @staticmethod
    def extract_text_from_url(url: str) -> Dict[str, str]:
        """Extract text content from a URL."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract title
            title = soup.find("title")
            title_text = title.get_text() if title else "Untitled"
            
            # Extract main content (try common article selectors)
            content_selectors = [
                "article",
                ".article-content",
                ".post-content",
                "#article-body",
                "main",
                ".content"
            ]
            
            content = ""
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text(separator="\n", strip=True)
                    break
            
            # Fallback to body if no specific content found
            if not content:
                body = soup.find("body")
                if body:
                    content = body.get_text(separator="\n", strip=True)
            
            # Clean up content
            content = re.sub(r"\s+", " ", content)
            content = content.strip()
            
            return {
                "title": title_text,
                "content": content,
                "url": url,
                "success": True
            }
        except Exception as e:
            return {
                "title": "",
                "content": "",
                "url": url,
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def process_urls(urls: List[str]) -> List[Dict[str, str]]:
        """Process multiple URLs and extract text."""
        results = []
        for url in urls:
            if url.strip():
                result = NewsService.extract_text_from_url(url.strip())
                results.append(result)
        return results
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into chunks with overlap."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks

