from ddgs import DDGS

def search_tool(query: str) -> str:
    try:
        results = DDGS().text(query, max_results=100)
            
        if not results:
            return "No results found."
            
        formatted_output = []
        for r in results:
            formatted_output.append(
                f"Title: {r.get('title')}\nURL: {r.get('href')}\nSnippet: {r.get('body')}"
            )
            
        return "\n\n".join(formatted_output)
    except Exception as e:
        return f"Error performing search: {str(e)}"
