"""Tool/function calling service for LLM interactions."""
from typing import Dict, List, Any, Optional
from .search_service import SearchService
import json
import logging

logger = logging.getLogger(__name__)


class ToolService:
    """Service for managing LLM tool calls."""
    
    # Define available tools
    TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "search_internet",
                "description": "Search the internet for current information, news, facts, or any query. Use this when you need up-to-date information that might not be in your training data.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to look up on the internet"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]
    
    @staticmethod
    def get_tools() -> List[Dict[str, Any]]:
        """Get list of available tools."""
        return ToolService.TOOLS
    
    @staticmethod
    def execute_tool(tool_name: str, arguments: Dict[str, Any], search_api_key: Optional[str] = None) -> str:
        """Execute a tool call and return the result."""
        try:
            if tool_name == "search_internet":
                query = arguments.get("query", "")
                if not query:
                    return "Error: Search query is required"
                
                results = SearchService.search(query, api_key=search_api_key, max_results=5)
                return SearchService.format_search_results(results)
            else:
                return f"Error: Unknown tool '{tool_name}'"
        except Exception as e:
            logger.error(f"Tool execution error: {str(e)}", exc_info=True)
            return f"Error executing tool: {str(e)}"
    
    @staticmethod
    def process_tool_calls(
        tool_calls: List[Dict[str, Any]],
        search_api_key: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Process multiple tool calls and return results."""
        tool_results = []
        
        for tool_call in tool_calls:
            tool_id = tool_call.get("id", "")
            function = tool_call.get("function", {})
            tool_name = function.get("name", "")
            arguments_str = function.get("arguments", "{}")
            
            try:
                arguments = json.loads(arguments_str) if isinstance(arguments_str, str) else arguments_str
            except json.JSONDecodeError:
                arguments = {}
            
            result = ToolService.execute_tool(tool_name, arguments, search_api_key)
            
            tool_results.append({
                "tool_call_id": tool_id,
                "role": "tool",
                "name": tool_name,
                "content": result
            })
        
        return tool_results

