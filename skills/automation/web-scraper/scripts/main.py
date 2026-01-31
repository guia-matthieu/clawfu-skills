#!/usr/bin/env python3
"""
Web Scraper - Extract structured data from websites.

Usage:
    python main.py scrape https://example.com --selector "h1,h2,p"
    python main.py links https://example.com --internal-only
    python main.py emails https://example.com
    python main.py structured https://example.com --schema article
"""

import click
from pathlib import Path
from typing import Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import json
import csv
import time


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; MarketingBot/1.0; +https://example.com/bot)'
}


def fetch_page(url: str) -> BeautifulSoup:
    """Fetch and parse webpage."""
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'lxml')


def is_internal_link(link: str, base_domain: str) -> bool:
    """Check if link is internal."""
    if not link:
        return False
    parsed = urlparse(link)
    if not parsed.netloc:
        return True  # Relative link
    return base_domain in parsed.netloc


@click.group()
def cli():
    """Web Scraper - Extract data from websites."""
    pass


@cli.command()
@click.argument('url')
@click.option('--selector', '-s', required=True, help='CSS selector(s)')
@click.option('--attribute', '-a', help='Extract specific attribute')
@click.option('--output', '-o', type=click.Path(), help='Output file')
@click.option('--format', '-f', 'output_format', default='text',
              type=click.Choice(['text', 'json', 'csv']))
def scrape(url: str, selector: str, attribute: Optional[str],
           output: Optional[str], output_format: str):
    """Scrape elements matching CSS selector."""
    click.echo("\n  Web Scraper")
    click.echo("  " + "=" * 40)
    click.echo(f"  URL: {url}")
    click.echo(f"  Selector: {selector}")

    soup = fetch_page(url)
    elements = soup.select(selector)

    click.echo(f"  Found: {len(elements)} elements")

    results = []
    for el in elements:
        if attribute:
            value = el.get(attribute, '')
        else:
            value = el.get_text(strip=True)
        if value:
            results.append({
                'tag': el.name,
                'text': value[:500],
                'class': ' '.join(el.get('class', [])),
            })

    # Display results
    click.echo("\n  Results")
    click.echo("  " + "-" * 40)
    for i, r in enumerate(results[:20], 1):
        click.echo(f"  {i}. {r['text'][:80]}{'...' if len(r['text']) > 80 else ''}")

    if len(results) > 20:
        click.echo(f"  ... and {len(results) - 20} more")

    # Save output
    if output:
        output_path = Path(output)
        if output_format == 'json':
            output_path.write_text(json.dumps(results, indent=2))
        elif output_format == 'csv':
            with open(output_path, 'w', newline='') as f:
                if results:
                    writer = csv.DictWriter(f, fieldnames=results[0].keys())
                    writer.writeheader()
                    writer.writerows(results)
        else:
            output_path.write_text('\n'.join(r['text'] for r in results))
        click.echo(f"\n  Saved: {output_path}")


@cli.command()
@click.argument('url')
@click.option('--internal-only', '-i', is_flag=True, help='Only internal links')
@click.option('--output', '-o', type=click.Path(), help='Output file')
def links(url: str, internal_only: bool, output: Optional[str]):
    """Extract all links from page."""
    click.echo("\n  Link Extractor")
    click.echo("  " + "=" * 40)
    click.echo(f"  URL: {url}")

    soup = fetch_page(url)
    base_domain = urlparse(url).netloc

    all_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        full_url = urljoin(url, href)
        text = a.get_text(strip=True)[:100]

        is_internal = is_internal_link(full_url, base_domain)

        if internal_only and not is_internal:
            continue

        all_links.append({
            'url': full_url,
            'text': text,
            'internal': is_internal
        })

    # Deduplicate
    seen = set()
    unique_links = []
    for link in all_links:
        if link['url'] not in seen:
            seen.add(link['url'])
            unique_links.append(link)

    internal_count = sum(1 for item in unique_links if item['internal'])
    external_count = len(unique_links) - internal_count

    click.echo(f"\n  Found {len(unique_links)} unique links")
    click.echo(f"  Internal: {internal_count}")
    click.echo(f"  External: {external_count}")

    click.echo("\n  Sample Links")
    click.echo("  " + "-" * 40)
    for link in unique_links[:15]:
        marker = "↳" if link['internal'] else "↗"
        click.echo(f"  {marker} {link['url'][:60]}")

    if output:
        output_path = Path(output)
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['url', 'text', 'internal'])
            writer.writeheader()
            writer.writerows(unique_links)
        click.echo(f"\n  Saved: {output_path}")


@cli.command()
@click.argument('url')
@click.option('--depth', '-d', default=1, help='Crawl depth')
@click.option('--output', '-o', type=click.Path(), help='Output file')
def emails(url: str, depth: int, output: Optional[str]):
    """Extract email addresses from page."""
    click.echo("\n  Email Extractor")
    click.echo("  " + "=" * 40)
    click.echo(f"  URL: {url}")
    click.echo(f"  Depth: {depth}")

    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    all_emails = set()
    visited = set()

    def extract_from_page(page_url: str, current_depth: int):
        if page_url in visited or current_depth > depth:
            return
        visited.add(page_url)

        try:
            soup = fetch_page(page_url)
            text = soup.get_text()

            # Find emails in text
            found = re.findall(email_pattern, text)
            all_emails.update(found)

            # Check mailto links
            for a in soup.find_all('a', href=True):
                href = a['href']
                if href.startswith('mailto:'):
                    email = href.replace('mailto:', '').split('?')[0]
                    all_emails.add(email)

            # Crawl internal links
            if current_depth < depth:
                base_domain = urlparse(url).netloc
                for a in soup.find_all('a', href=True):
                    link = urljoin(page_url, a['href'])
                    if is_internal_link(link, base_domain):
                        time.sleep(0.5)  # Rate limiting
                        extract_from_page(link, current_depth + 1)

        except Exception as e:
            click.echo(f"  Error: {page_url}: {e}")

    extract_from_page(url, 0)

    # Filter out common false positives
    filtered_emails = [
        e for e in all_emails
        if not e.endswith('.png') and not e.endswith('.jpg')
        and '@example' not in e and 'noreply' not in e.lower()
    ]

    click.echo(f"\n  Found {len(filtered_emails)} emails")
    click.echo("  " + "-" * 40)
    for email in sorted(filtered_emails):
        click.echo(f"  • {email}")

    if output:
        output_path = Path(output)
        output_path.write_text('\n'.join(sorted(filtered_emails)))
        click.echo(f"\n  Saved: {output_path}")


@cli.command()
@click.argument('url')
@click.option('--schema', '-s', required=True,
              type=click.Choice(['article', 'product', 'business', 'generic']))
@click.option('--output', '-o', type=click.Path(), help='Output file')
def structured(url: str, schema: str, output: Optional[str]):
    """Extract structured data based on schema type."""
    click.echo("\n  Structured Data Extractor")
    click.echo("  " + "=" * 40)
    click.echo(f"  URL: {url}")
    click.echo(f"  Schema: {schema}")

    soup = fetch_page(url)
    data = {'url': url, 'schema': schema}

    if schema == 'article':
        data['title'] = soup.find('h1').get_text(strip=True) if soup.find('h1') else ''

        # Try common meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', meta.get('property', '')).lower()
            if 'author' in name:
                data['author'] = meta.get('content', '')
            elif 'date' in name or 'published' in name:
                data['date'] = meta.get('content', '')
            elif 'description' in name:
                data['description'] = meta.get('content', '')

        # Get article content
        article = soup.find('article') or soup.find('main') or soup.find('body')
        if article:
            paragraphs = article.find_all('p')
            data['content'] = ' '.join(p.get_text(strip=True) for p in paragraphs)
            data['word_count'] = len(data['content'].split())

    elif schema == 'product':
        data['name'] = soup.find('h1').get_text(strip=True) if soup.find('h1') else ''

        # Look for price patterns
        price_pattern = r'\$[\d,]+\.?\d*'
        prices = re.findall(price_pattern, soup.get_text())
        data['prices'] = list(set(prices))

        # Look for images
        images = soup.find_all('img', src=True)
        data['images'] = [urljoin(url, img['src']) for img in images[:5]]

    elif schema == 'business':
        # Extract contact info
        data['phones'] = re.findall(r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}',
                                     soup.get_text())
        data['emails'] = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                                     soup.get_text())

        # Look for address
        address_el = soup.find(class_=re.compile(r'address', re.I))
        if address_el:
            data['address'] = address_el.get_text(strip=True)

    else:  # generic
        data['title'] = soup.title.string if soup.title else ''
        data['headings'] = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])][:10]
        data['meta_description'] = ''
        for meta in soup.find_all('meta'):
            if meta.get('name', '').lower() == 'description':
                data['meta_description'] = meta.get('content', '')

    # Display
    click.echo("\n  Extracted Data")
    click.echo("  " + "-" * 40)
    for key, value in data.items():
        if isinstance(value, str) and len(value) > 100:
            value = value[:100] + '...'
        elif isinstance(value, list) and len(value) > 5:
            value = value[:5] + ['...']
        click.echo(f"  {key}: {value}")

    # Save
    if output:
        output_path = Path(output)
        output_path.write_text(json.dumps(data, indent=2))
        click.echo(f"\n  Saved: {output_path}")
    else:
        default_output = Path(f"scraped_{schema}.json")
        default_output.write_text(json.dumps(data, indent=2))
        click.echo(f"\n  Saved: {default_output}")


if __name__ == "__main__":
    cli()
