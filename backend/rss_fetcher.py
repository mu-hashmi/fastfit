"""RSS feed fetcher for clothing brand new releases."""
from typing import List, Dict, Any
import httpx
import feedparser
from datetime import datetime
import hashlib
import re
from config import config

class RSSFetcher:
    """Fetches products from fashion brand RSS feeds."""
    
    def __init__(self):
        """Initialize RSS fetcher."""
        self.client = httpx.Client(timeout=30.0)
        self.processed_ids = set()  # Track processed products to avoid duplicates
    
    def fetch_feed(self, feed_url: str) -> List[Dict[str, Any]]:
        """Fetch and parse a single RSS feed."""
        products = []
        try:
            response = self.client.get(feed_url)
            response.raise_for_status()
            
            feed = feedparser.parse(response.text)
            
            for entry in feed.entries:
                # Generate unique ID from entry link or title
                product_id = self._generate_id(entry)
                
                # Skip if already processed
                if product_id in self.processed_ids:
                    continue
                
                # Extract product information
                raw_description = entry.get("summary", entry.get("description", ""))
                cleaned_description = self._strip_html(raw_description)
                
                product = {
                    "id": product_id,
                    "name": entry.get("title", ""),
                    "description": cleaned_description,
                    "brand": self._extract_brand_from_feed(feed_url, entry),
                    "product_url": entry.get("link", ""),
                    "image_url": self._extract_image(entry),
                    "published_date": self._parse_date(entry.get("published", "")),
                    "source_feed": feed_url
                }
                
                products.append(product)
                self.processed_ids.add(product_id)
        
        except Exception as e:
            print(f"Error fetching RSS feed {feed_url}: {e}")
        
        return products
    
    def fetch_all_feeds(self) -> List[Dict[str, Any]]:
        """Fetch products from all configured RSS feeds."""
        all_products = []
        
        for feed_url in config.RSS_FEEDS:
            products = self.fetch_feed(feed_url)
            all_products.extend(products)
        
        return all_products
    
    def _generate_id(self, entry: Dict[str, Any]) -> str:
        """Generate unique ID for a product."""
        # Use link if available, otherwise use title
        unique_string = entry.get("link", "") or entry.get("title", "")
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    def _extract_brand_from_feed(self, feed_url: str, entry: Dict[str, Any]) -> str:
        """Extract brand name from feed URL or entry."""
        # Try to extract from feed URL
        if "adidas" in feed_url.lower():
            return "Adidas"
        elif "hypebeast" in feed_url.lower():
            return "HYPEBEAST"
        elif "luxury" in feed_url.lower():
            return "Luxury Brands"
        
        # Try to extract from entry title or description
        title = entry.get("title", "").lower()
        if "adidas" in title:
            return "Adidas"
        elif "nike" in title:
            return "Nike"
        elif "zara" in title:
            return "Zara"
        
        return "Unknown Brand"
    
    def _extract_image(self, entry: Dict[str, Any]) -> str:
        """Extract image URL from RSS entry."""
        # Check for media content
        if "media_content" in entry:
            for media in entry.media_content:
                if media.get("type", "").startswith("image"):
                    return media.get("url", "")
        
        # Check for media thumbnail
        if "media_thumbnail" in entry:
            return entry.media_thumbnail[0].get("url", "")
        
        # Check for enclosures
        if "enclosures" in entry:
            for enclosure in entry.enclosures:
                if enclosure.get("type", "").startswith("image"):
                    return enclosure.get("href", "")
        
        # Check for image in summary/description
        summary = entry.get("summary", entry.get("description", ""))
        if summary and "<img" in summary:
            # Simple extraction - in production, use proper HTML parsing
            import re
            img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', summary)
            if img_match:
                return img_match.group(1)
        
        return ""
    
    def _strip_html(self, html_text: str) -> str:
        """Strip HTML tags and decode HTML entities from text."""
        if not html_text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html_text)
        
        # Decode common HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        text = text.replace('&apos;', "'")
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Limit length to reasonable size
        if len(text) > 500:
            text = text[:500] + "..."
        
        return text
    
    def _parse_date(self, date_string: str) -> str:
        """Parse date string to ISO format."""
        try:
            if not date_string:
                return datetime.now().isoformat()
            
            # feedparser handles most date formats
            parsed = feedparser._parse_date(date_string)
            if parsed:
                return datetime(*parsed[:6]).isoformat()
        except:
            pass
        
        return datetime.now().isoformat()

# Global fetcher instance
rss_fetcher = RSSFetcher()

