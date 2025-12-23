import httpx
import asyncio
from bs4 import BeautifulSoup

async def test_fetch():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        r = await client.get('https://www.frbsf.org/research-and-insights/publications/economic-letter/')
        print("Status:", r.status_code)
        print("\nFirst 2000 characters:")
        print(r.text[:2000])
        print("\n\nLooking for articles...")
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Try different selectors
        articles = soup.find_all('article')
        print(f"Found {len(articles)} <article> tags")
        
        posts = soup.find_all('article', class_='post')
        print(f"Found {len(posts)} <article class='post'> tags")
        
        divs = soup.find_all('div', class_='economic-letter')
        print(f"Found {len(divs)} <div class='economic-letter'> tags")
        
        # Look for any links that might be letters
        links = soup.find_all('a', href=True)
        letter_links = [a for a in links if 'economic-letter' in a.get('href', '')]
        print(f"Found {len(letter_links)} links containing 'economic-letter'")
        
        if letter_links:
            print("\nFirst few letter links:")
            for link in letter_links[:5]:
                print(f"  - {link.get_text(strip=True)[:60]}: {link['href']}")

asyncio.run(test_fetch())
