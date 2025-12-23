"""Internet search service."""
import requests
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class SearchService:
    """Service for internet search operations."""
    
    @staticmethod
    def search_duckduckgo(query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """Search using DuckDuckGo (no API key required)."""
        try:
            results = []
            
            # Use duckduckgo-search library if available (better results)
            if DDGS_AVAILABLE:
                try:
                    with DDGS() as ddgs:
                        search_results = list(ddgs.text(query, max_results=max_results))
                        for result in search_results:
                            results.append({
                                "title": result.get("title", ""),
                                "snippet": result.get("body", ""),
                                "url": result.get("href", ""),
                                "source": "DuckDuckGo"
                            })
                    if results:
                        return results
                except Exception as e:
                    logger.warning(f"DuckDuckGo library search failed: {e}, trying fallback")
            
            # Fallback: Use HTML scraping
            try:
                html_url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
                html_response = requests.get(html_url, timeout=10, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                })
                
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html_response.content, "html.parser")
                
                for result in soup.select(".result")[:max_results]:
                    title_elem = result.select_one(".result__a")
                    snippet_elem = result.select_one(".result__snippet")
                    
                    if title_elem and snippet_elem:
                        results.append({
                            "title": title_elem.get_text(strip=True),
                            "snippet": snippet_elem.get_text(strip=True),
                            "url": title_elem.get("href", ""),
                            "source": "DuckDuckGo"
                        })
            except Exception as e:
                logger.warning(f"DuckDuckGo HTML fallback failed: {e}")
            
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {str(e)}")
            return []
    
    @staticmethod
    def search_serper(query: str, api_key: Optional[str] = None, max_results: int = 5) -> List[Dict[str, str]]:
        """Search using Serper API (requires API key)."""
        if not api_key:
            return SearchService.search_duckduckgo(query, max_results)
        
        try:
            url = "https://google.serper.dev/search"
            headers = {
                "X-API-KEY": api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "q": query,
                "num": max_results
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("organic", [])[:max_results]:
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "url": item.get("link", ""),
                    "source": "Serper"
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Serper search error: {str(e)}")
            # Fallback to DuckDuckGo
            return SearchService.search_duckduckgo(query, max_results)
    
    @staticmethod
    def search(query: str, api_key: Optional[str] = None, max_results: int = 5) -> List[Dict[str, str]]:
        """Search the internet. Uses Serper if API key provided, otherwise DuckDuckGo."""
        if api_key:
            return SearchService.search_serper(query, api_key, max_results)
        else:
            return SearchService.search_duckduckgo(query, max_results)
    
    @staticmethod
    def format_search_results(results: List[Dict[str, str]]) -> str:
        """Format search results as a string for LLM consumption."""
        if not results:
            return "No search results found."
        
        formatted = "Search Results:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result['title']}\n"
            formatted += f"   URL: {result['url']}\n"
            formatted += f"   {result['snippet']}\n\n"
        
        return formatted

