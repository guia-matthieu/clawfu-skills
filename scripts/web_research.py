"""
Web Research Module
Search + Scrape via Brightdata or fallback methods
"""

import re
import httpx
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

from config import config


@dataclass
class SearchResult:
    """Search result item."""
    title: str
    url: str
    snippet: str
    domain: str


@dataclass
class ScrapedContent:
    """Scraped page content."""
    url: str
    title: str
    content: str
    word_count: int
    success: bool
    error: Optional[str] = None


class WebResearcher:
    """Web research via search and scraping."""

    def __init__(self):
        self.config = config.brightdata
        self.research_config = config.research

    def search_google(self, query: str, num_results: int = 10) -> list[SearchResult]:
        """
        Search Google via Brightdata SERP API.
        Falls back to DuckDuckGo HTML if Brightdata unavailable.
        """
        # Try Brightdata SERP first
        if self.config.api_key:
            try:
                return self._search_brightdata(query, num_results)
            except Exception as e:
                print(f"Brightdata search failed: {e}, falling back to DDG")

        # Fallback to DuckDuckGo HTML scraping
        return self._search_duckduckgo(query, num_results)

    def _search_brightdata(self, query: str, num_results: int) -> list[SearchResult]:
        """Search via Brightdata SERP API."""
        # Note: This would use the actual Brightdata SERP API
        # For now, return empty to trigger fallback
        raise NotImplementedError("Brightdata SERP integration pending")

    def _search_duckduckgo(self, query: str, num_results: int) -> list[SearchResult]:
        """Fallback search via DuckDuckGo HTML."""
        try:
            from urllib.parse import unquote

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
            params = {"q": query, "t": "h_", "ia": "web"}

            with httpx.Client(timeout=30, follow_redirects=True) as client:
                response = client.get(
                    "https://html.duckduckgo.com/html/",
                    params=params,
                    headers=headers,
                )
                response.raise_for_status()

            results = []
            # DDG wraps URLs in redirect links, extract the actual URL
            # Pattern: href="//duckduckgo.com/l/?uddg=https%3A%2F%2Factual-url.com..."
            pattern = r'<a rel="nofollow" class="result__a" href="[^"]*uddg=([^&"]+)[^"]*"[^>]*>([^<]+)</a>'
            snippet_pattern = r'<a class="result__snippet"[^>]*>([^<]+)</a>'

            matches = re.findall(pattern, response.text)
            snippets = re.findall(snippet_pattern, response.text)

            for i, (encoded_url, title) in enumerate(matches[:num_results * 2]):
                # Decode the URL
                url = unquote(encoded_url)

                # Ensure URL has protocol
                if not url.startswith('http'):
                    continue

                domain = urlparse(url).netloc.replace("www.", "")
                snippet = snippets[i] if i < len(snippets) else ""

                # Filter blocked domains
                if any(blocked in domain for blocked in self.config.blocked_domains):
                    continue

                # Skip if we already have this domain
                if any(r.domain == domain for r in results):
                    continue

                results.append(SearchResult(
                    title=title.strip(),
                    url=url,
                    snippet=snippet.strip(),
                    domain=domain,
                ))

                if len(results) >= num_results:
                    break

            return results

        except Exception as e:
            print(f"DuckDuckGo search failed: {e}")
            return []

    def scrape_url(self, url: str) -> ScrapedContent:
        """
        Scrape URL content.
        Uses Brightdata if available, falls back to direct request.
        """
        domain = urlparse(url).netloc.replace("www.", "")

        # Try Brightdata for complex sites
        if self.config.api_key and self._needs_brightdata(domain):
            try:
                return self._scrape_brightdata(url)
            except Exception as e:
                print(f"Brightdata scrape failed: {e}, trying direct")

        # Direct request for simple sites
        return self._scrape_direct(url)

    def _needs_brightdata(self, domain: str) -> bool:
        """Check if domain likely needs Brightdata (has bot protection)."""
        protected_domains = [
            "medium.com", "substack.com", "linkedin.com",
            "twitter.com", "x.com", "facebook.com",
        ]
        return any(d in domain for d in protected_domains)

    def _scrape_brightdata(self, url: str) -> ScrapedContent:
        """Scrape via Brightdata Web Unlocker."""
        # This would integrate with Brightdata's Web Unlocker API
        raise NotImplementedError("Brightdata scraping integration pending")

    def _scrape_direct(self, url: str) -> ScrapedContent:
        """Direct HTTP scraping for simple sites."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }

            with httpx.Client(timeout=30, follow_redirects=True) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()

            html = response.text

            # Extract title
            title_match = re.search(r'<title>([^<]+)</title>', html, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else ""

            # Extract main content (simple extraction)
            content = self._extract_content(html)

            # Check minimum length
            if len(content) < self.research_config.min_content_length:
                return ScrapedContent(
                    url=url, title=title, content="",
                    word_count=0, success=False,
                    error="Content too short"
                )

            # Truncate if too long
            if len(content) > self.research_config.max_content_length:
                content = content[:self.research_config.max_content_length]

            word_count = len(content.split())

            return ScrapedContent(
                url=url, title=title, content=content,
                word_count=word_count, success=True
            )

        except Exception as e:
            return ScrapedContent(
                url=url, title="", content="",
                word_count=0, success=False,
                error=str(e)
            )

    def _extract_content(self, html: str) -> str:
        """Extract readable content from HTML."""
        # Remove scripts, styles, nav, footer
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<nav[^>]*>.*?</nav>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<footer[^>]*>.*?</footer>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<header[^>]*>.*?</header>', '', html, flags=re.DOTALL | re.IGNORECASE)

        # Remove all HTML tags
        text = re.sub(r'<[^>]+>', ' ', html)

        # Clean whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        # Decode HTML entities
        import html as html_module
        text = html_module.unescape(text)

        return text

    def research_topic(
        self,
        expert: str,
        topic: str,
        max_sources: int = 5
    ) -> list[ScrapedContent]:
        """
        Complete research pipeline for an expert/topic.

        Args:
            expert: Expert name (e.g., "Russell Brunson")
            topic: Topic/book (e.g., "DotCom Secrets")
            max_sources: Maximum sources to collect

        Returns:
            List of successfully scraped content
        """
        # Generate search queries
        queries = [
            f"{expert} {topic} summary",
            f"{expert} {topic} key principles",
            f"{expert} {topic} framework",
            f"{topic} book notes",
            f"{expert} methodology",
        ]

        # Collect unique URLs
        seen_urls = set()
        all_results = []

        for query in queries:
            results = self.search_google(query, num_results=5)
            for r in results:
                if r.url not in seen_urls:
                    seen_urls.add(r.url)
                    all_results.append(r)

        # Prioritize known good domains
        def domain_priority(result: SearchResult) -> int:
            for i, domain in enumerate(self.config.priority_domains):
                if domain in result.domain:
                    return i
            return 100

        all_results.sort(key=domain_priority)

        # Scrape top results
        scraped = []
        for result in all_results[:max_sources * 2]:  # Try more in case some fail
            if len(scraped) >= max_sources:
                break

            print(f"  Scraping: {result.domain} - {result.title[:50]}...")
            content = self.scrape_url(result.url)

            if content.success:
                scraped.append(content)
                print(f"    ✓ {content.word_count} words")
            else:
                print(f"    ✗ {content.error}")

        return scraped


# Singleton
researcher = WebResearcher()
