"""Web scraper service for FRBSF economic letters."""

import logging
from typing import List, Optional, Dict
from datetime import datetime
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class LetterData:
    """Data class for scraped letter information."""
    
    def __init__(self, title: str, url: str, publication_date: str, 
                 summary: Optional[str], content: str):
        self.title = title
        self.url = url
        self.publication_date = publication_date
        self.summary = summary
        self.content = content


class ScraperService:
    """Service for scraping economic letters from FRBSF website."""
    
    def __init__(self, base_url: str, timeout: int = 30, max_retries: int = 3):
        """
        Initialize the scraper service.
        
        Args:
            base_url: Base URL for FRBSF economic letters
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
    
    async def fetch_letters_page(self, page: int = 1) -> List[LetterData]:
        """
        Fetch letters from a specific page.
        
        Args:
            page: Page number to fetch (1-indexed)
            
        Returns:
            List of LetterData objects
        """
        try:
            # Construct URL with pagination
            if page == 1:
                url = self.base_url
            else:
                url = f"{self.base_url}/page/{page}"
            
            logger.info(f"Fetching letters from page {page}: {url}")
            
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                html = response.text
                letters = self.parse_letter_list(html)
                
                logger.info(f"Found {len(letters)} letters on page {page}")
                return letters
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching page {page}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching page {page}: {e}")
            return []
    
    def parse_letter_list(self, html: str) -> List[LetterData]:
        """
        Parse the letter list HTML to extract letter metadata.
        
        Args:
            html: HTML content of the letter list page
            
        Returns:
            List of LetterData objects
        """
        letters = []
        seen_urls = set()
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find all links that point to economic letters
            all_links = soup.find_all('a', href=True)
            
            for link in all_links:
                try:
                    url = link.get('href', '')
                    
                    # Skip if not an economic letter URL or if we've seen it
                    if not url or 'economic-letter' not in url:
                        continue
                    
                    # Make URL absolute if relative
                    if not url.startswith('http'):
                        url = f"https://www.frbsf.org{url}"
                    
                    # Skip pagination links and the main page
                    if '/page/' in url or url.endswith('/economic-letter/') or url.endswith('/economic-letter'):
                        continue
                    
                    # Skip if we've already seen this URL
                    if url in seen_urls:
                        continue
                    
                    seen_urls.add(url)
                    
                    # Extract title from link text
                    title = link.get_text(strip=True)
                    
                    # Skip if title is too short or generic
                    if not title or len(title) < 10 or title.lower() in ['read the economic letter', 'economic letter']:
                        continue
                    
                    # Try to find parent container for more info
                    parent = link.find_parent(['div', 'section', 'li'])
                    
                    # Extract publication date from URL (format: /YYYY/MM/)
                    publication_date = ''
                    import re
                    date_match = re.search(r'/(\d{4})/(\d{2})/', url)
                    if date_match:
                        year, month = date_match.groups()
                        publication_date = f"{year}-{month}-01"
                    
                    # Try to find summary/excerpt in parent
                    summary = None
                    if parent:
                        # Look for paragraph or excerpt
                        p_elem = parent.find('p')
                        if p_elem and p_elem != link:
                            summary = p_elem.get_text(strip=True)
                    
                    # Use title as initial content
                    content = summary or title
                    
                    letter = LetterData(
                        title=title,
                        url=url,
                        publication_date=publication_date,
                        summary=summary,
                        content=content
                    )
                    letters.append(letter)
                    
                except Exception as e:
                    logger.warning(f"Error parsing link: {e}")
                    continue
            
            logger.info(f"Parsed {len(letters)} unique letters from HTML")
            
        except Exception as e:
            logger.error(f"Error parsing letter list HTML: {e}")
        
        return letters
    
    async def fetch_letter_content(self, url: str) -> str:
        """
        Fetch the full content of a specific letter.
        
        Args:
            url: URL of the letter
            
        Returns:
            Full letter content as text
        """
        try:
            logger.info(f"Fetching letter content from: {url}")
            
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                html = response.text
                content = self.parse_letter_content(html)
                
                return content
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching letter content: {e}")
            return ""
        except Exception as e:
            logger.error(f"Error fetching letter content: {e}")
            return ""
    
    def parse_letter_content(self, html: str) -> str:
        """
        Parse the letter detail page to extract full content.
        
        Args:
            html: HTML content of the letter detail page
            
        Returns:
            Letter content as text
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find the main content area
            content_elem = (
                soup.find('div', class_='entry-content') or
                soup.find('article') or
                soup.find('main')
            )
            
            if content_elem:
                # Remove script and style elements
                for script in content_elem(['script', 'style']):
                    script.decompose()
                
                # Get text content
                content = content_elem.get_text(separator='\n', strip=True)
                return content
            
            return ""
            
        except Exception as e:
            logger.error(f"Error parsing letter content: {e}")
            return ""
