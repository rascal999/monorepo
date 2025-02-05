from smolagents import tool

@tool
def web_search(query: str) -> str:
    """
    Perform a web search using DuckDuckGo.

    Args:
        query: The search query.

    Returns:
        A string containing search results.
    """
    try:
        from duckduckgo_search import DDGS
        ddgs = DDGS()
        results = ddgs.text(query, max_results=3)
        if not results:
            return f"No results found for: {query}"
            
        formatted_results = []
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            body = result.get('body', 'No content')
            link = result.get('link', 'No link')
            formatted_results.append(f"{i}. {title}\n   {body}\n   Source: {link}")
            
        return "Search Results:\n\n" + "\n\n".join(formatted_results)
    except Exception as e:
        return f"Error performing web search: {str(e)}"

@tool
def visit_webpage(url: str) -> str:
    """
    Visit a webpage and extract its content.

    Args:
        url: The URL of the webpage to visit.

    Returns:
        A string containing the webpage content.
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return f"Content from {url}:\n\n{text[:1500]}..." if len(text) > 1500 else text
    except Exception as e:
        return f"Error visiting webpage: {str(e)}"