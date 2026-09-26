def extract_json(response: str) -> str:
    """Extract the first JSON object from the response string."""
    try:
        start = response.find('{')
        if start == -1:
            return ""
        
        count = 0
        for i in range(start, len(response)):
            if response[i] == '{':
                count += 1
            elif response[i] == '}':
                count -= 1
                if count == 0:
                    return response[start:i+1]
    except Exception as e:
        print(f"Error extracting JSON: {e}")
        return ""
    return ""