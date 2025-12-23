"""Take screenshots of the application for documentation."""

import asyncio
from playwright.async_api import async_playwright
import os

async def take_screenshots():
    """Capture screenshots of the application."""
    
    # Create screenshots directory
    os.makedirs('screenshots', exist_ok=True)
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        # Navigate to the application
        await page.goto('http://localhost:8000')
        await page.wait_for_timeout(2000)  # Wait for page to load
        
        # Screenshot 1: Main page with letter list
        await page.screenshot(path='screenshots/01-letter-list.png', full_page=True)
        print("✓ Captured: Letter list page")
        
        # Click on first letter
        await page.click('.letter-card')
        await page.wait_for_timeout(2000)
        
        # Screenshot 2: Letter detail page
        await page.screenshot(path='screenshots/02-letter-detail.png', full_page=True)
        print("✓ Captured: Letter detail page")
        
        # Type a question
        await page.fill('textarea', 'What are the main findings of this economic letter?')
        await page.wait_for_timeout(500)
        
        # Screenshot 3: Question input
        await page.screenshot(path='screenshots/03-question-input.png', full_page=True)
        print("✓ Captured: Question input")
        
        # Submit question
        await page.click('button:has-text("Ask Question")')
        await page.wait_for_timeout(8000)  # Wait for AI response
        
        # Screenshot 4: AI response with markdown
        await page.screenshot(path='screenshots/04-ai-response.png', full_page=True)
        print("✓ Captured: AI response with markdown")
        
        # Go back to list
        await page.click('button:has-text("Back to List")')
        await page.wait_for_timeout(1000)
        
        # Screenshot 5: Full letter list
        await page.screenshot(path='screenshots/05-full-list.png', full_page=True)
        print("✓ Captured: Full letter list")
        
        await browser.close()
        print("\n✅ All screenshots captured successfully!")

if __name__ == "__main__":
    asyncio.run(take_screenshots())
