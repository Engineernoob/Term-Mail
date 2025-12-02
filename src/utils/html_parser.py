"""HTML to plain text conversion utilities"""

from bs4 import BeautifulSoup
import re


def html_to_text(html_content: str) -> str:
    """
    Convert HTML email content to readable plain text.
    
    Args:
        html_content: HTML string to convert
        
    Returns:
        Plain text representation
    """
    if not html_content:
        return ""
    
    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Convert <br> tags to newlines
    for br in soup.find_all("br"):
        br.replace_with("\n")
    
    # Convert <p> tags to newlines
    for p in soup.find_all("p"):
        p.append("\n")
    
    # Convert <div> tags to newlines
    for div in soup.find_all("div"):
        div.append("\n")
    
    # Get text content
    text = soup.get_text()
    
    # Clean up whitespace
    lines = [line.strip() for line in text.splitlines()]
    text = "\n".join(line for line in lines if line)
    
    # Remove excessive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

