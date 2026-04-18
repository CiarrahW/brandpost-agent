import os
import json
import requests
from agents import function_tool


@function_tool
def search_trending_topics(query: str) -> str:
    """
    Search for current trending topics related to the given product or category.
    Returns a JSON string with a list of trending topics and their descriptions.
    """
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return "Error: SERPER_API_KEY not set"

    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "q": f"{query} trends 2025",
        "num": 5,
    }

    try:
        response = requests.post(
            "https://google.serper.dev/search",
            headers=headers,
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        topics = []
        for item in data.get("organic", [])[:5]:
            topics.append({
                "title": item.get("title", ""),
                "snippet": item.get("snippet", ""),
            })

        return json.dumps({"trending_topics": topics}, ensure_ascii=False)

    except Exception as e:
        return f"Error: {str(e)}"
