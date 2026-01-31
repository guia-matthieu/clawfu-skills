#!/usr/bin/env python3
"""
Content Repurposer - Transform long-form content into multiple formats.

Usage:
    python main.py repurpose transcript.txt --formats "twitter,linkedin"
    python main.py thread article.md --max-tweets 10
    python main.py quotes interview.txt --count 5
    python main.py hooks content.txt --count 10
"""

import click
from pathlib import Path
from typing import Optional
import os


def check_anthropic():
    """Check if anthropic is installed and API key is set."""
    try:
        import anthropic  # noqa: F401
        if not os.environ.get('ANTHROPIC_API_KEY'):
            return False, "ANTHROPIC_API_KEY not set"
        return True, None
    except ImportError:
        return False, "anthropic not installed"


def get_client():
    """Get Anthropic client."""
    import anthropic
    return anthropic.Anthropic()


def call_claude(prompt: str, max_tokens: int = 4096) -> str:
    """Call Claude API with prompt."""
    client = get_client()
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


FORMATS = ['twitter', 'linkedin', 'instagram', 'quotes', 'hooks', 'summary', 'newsletter']
STYLES = ['educational', 'inspirational', 'provocative', 'conversational', 'professional']


@click.group()
def cli():
    """Content Repurposer - Transform content into multiple formats."""
    ok, error = check_anthropic()
    if not ok:
        click.echo(f"Error: {error}")
        if "not installed" in error:
            click.echo("Run: pip install anthropic")
        else:
            click.echo("Set: export ANTHROPIC_API_KEY=your_key")
        raise SystemExit(1)


@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--formats', '-f', default='twitter,linkedin,quotes',
              help='Comma-separated formats or "all"')
@click.option('--style', '-s', default='educational',
              type=click.Choice(STYLES))
@click.option('--output', '-o', type=click.Path(), help='Output directory')
def repurpose(file: str, formats: str, style: str, output: Optional[str]):
    """Repurpose content into multiple formats."""
    input_path = Path(file)
    content = input_path.read_text()

    if formats == 'all':
        format_list = FORMATS
    else:
        format_list = [f.strip() for f in formats.split(',')]

    output_dir = Path(output) if output else input_path.parent / f"{input_path.stem}_repurposed"
    output_dir.mkdir(parents=True, exist_ok=True)

    click.echo("\n  Content Repurposer")
    click.echo("  " + "=" * 40)
    click.echo(f"  Input: {input_path.name}")
    click.echo(f"  Formats: {', '.join(format_list)}")
    click.echo(f"  Style: {style}")
    click.echo(f"  Output: {output_dir}")

    for fmt in format_list:
        click.echo(f"\n  Generating {fmt}...")

        if fmt == 'twitter':
            result = generate_thread(content, style, 12)
            output_file = output_dir / 'twitter_thread.md'
        elif fmt == 'linkedin':
            result = generate_linkedin(content, style)
            output_file = output_dir / 'linkedin_post.md'
        elif fmt == 'instagram':
            result = generate_instagram(content, style)
            output_file = output_dir / 'instagram_carousel.md'
        elif fmt == 'quotes':
            result = generate_quotes(content, style, 5)
            output_file = output_dir / 'quotes.md'
        elif fmt == 'hooks':
            result = generate_hooks(content, style, 5)
            output_file = output_dir / 'hooks.md'
        elif fmt == 'summary':
            result = generate_summary(content, style)
            output_file = output_dir / 'summary.md'
        elif fmt == 'newsletter':
            result = generate_newsletter(content, style)
            output_file = output_dir / 'newsletter.md'
        else:
            click.echo(f"    Unknown format: {fmt}")
            continue

        output_file.write_text(result)
        click.echo(f"    -> {output_file.name}")

    click.echo("\n  " + "-" * 40)
    click.echo(f"  [Done] Generated {len(format_list)} formats")
    click.echo(f"  Output: {output_dir}")


@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--max-tweets', '-m', default=12, help='Maximum tweets in thread')
@click.option('--style', '-s', default='educational', type=click.Choice(STYLES))
@click.option('--output', '-o', type=click.Path(), help='Output file')
def thread(file: str, max_tweets: int, style: str, output: Optional[str]):
    """Convert content to Twitter thread."""
    input_path = Path(file)
    content = input_path.read_text()

    click.echo("\n  Twitter Thread Generator")
    click.echo("  " + "=" * 40)
    click.echo(f"  Input: {input_path.name}")
    click.echo(f"  Max tweets: {max_tweets}")
    click.echo(f"  Style: {style}")

    click.echo("  Generating thread...")
    result = generate_thread(content, style, max_tweets)

    output_path = Path(output) if output else input_path.with_stem(f"{input_path.stem}_thread")
    output_path = output_path.with_suffix('.md')
    output_path.write_text(result)

    # Count tweets
    tweet_count = result.count('\n\n') + 1

    click.echo("\n  " + "-" * 40)
    click.echo(f"  [Done] Generated {tweet_count}-tweet thread")
    click.echo(f"  Output: {output_path}")


@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--count', '-c', default=5, help='Number of quotes')
@click.option('--style', '-s', default='inspirational', type=click.Choice(STYLES))
@click.option('--output', '-o', type=click.Path(), help='Output file')
def quotes(file: str, count: int, style: str, output: Optional[str]):
    """Extract quotable moments from content."""
    input_path = Path(file)
    content = input_path.read_text()

    click.echo("\n  Quote Extraction")
    click.echo("  " + "=" * 40)
    click.echo(f"  Input: {input_path.name}")
    click.echo(f"  Count: {count}")
    click.echo(f"  Style: {style}")

    click.echo("  Extracting quotes...")
    result = generate_quotes(content, style, count)

    output_path = Path(output) if output else input_path.with_stem(f"{input_path.stem}_quotes")
    output_path = output_path.with_suffix('.md')
    output_path.write_text(result)

    click.echo("\n  " + "-" * 40)
    click.echo(f"  [Done] Extracted {count} quotes")
    click.echo(f"  Output: {output_path}")


@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--count', '-c', default=10, help='Number of hooks')
@click.option('--style', '-s', default='curiosity',
              type=click.Choice(['curiosity', 'controversy', 'story', 'stat', 'question']))
@click.option('--output', '-o', type=click.Path(), help='Output file')
def hooks(file: str, count: int, style: str, output: Optional[str]):
    """Generate attention-grabbing hooks."""
    input_path = Path(file)
    content = input_path.read_text()

    click.echo("\n  Hook Generation")
    click.echo("  " + "=" * 40)
    click.echo(f"  Input: {input_path.name}")
    click.echo(f"  Count: {count}")
    click.echo(f"  Style: {style}")

    click.echo("  Generating hooks...")
    result = generate_hooks(content, style, count)

    output_path = Path(output) if output else input_path.with_stem(f"{input_path.stem}_hooks")
    output_path = output_path.with_suffix('.md')
    output_path.write_text(result)

    click.echo("\n  " + "-" * 40)
    click.echo(f"  [Done] Generated {count} hooks")
    click.echo(f"  Output: {output_path}")


def generate_thread(content: str, style: str, max_tweets: int) -> str:
    """Generate Twitter thread from content."""
    prompt = f"""Transform this content into a Twitter thread.

Style: {style}
Max tweets: {max_tweets}

Rules:
- First tweet should hook the reader (no "Thread:" prefix)
- Each tweet under 280 characters
- Number tweets like "1/" "2/" etc.
- End with a call to action or summary
- Make it conversational and engaging

Content:
{content[:8000]}

Output the thread in markdown, each tweet as a paragraph:"""

    return call_claude(prompt)


def generate_linkedin(content: str, style: str) -> str:
    """Generate LinkedIn post from content."""
    prompt = f"""Transform this content into a LinkedIn post.

Style: {style}

Rules:
- Strong opening hook (first 2 lines visible in feed)
- Use line breaks for readability
- 1200-1500 characters ideal
- End with a question or call to engagement
- Professional but not corporate

Content:
{content[:8000]}

Output the LinkedIn post:"""

    return call_claude(prompt)


def generate_instagram(content: str, style: str) -> str:
    """Generate Instagram carousel content."""
    prompt = f"""Transform this content into Instagram carousel slides.

Style: {style}

Rules:
- 10 slides maximum
- Slide 1: Attention-grabbing hook
- Slides 2-9: Key points (one idea per slide)
- Slide 10: Call to action
- Keep text short (fits on image)
- Think visually

Content:
{content[:8000]}

Output as numbered slides:"""

    return call_claude(prompt)


def generate_quotes(content: str, style: str, count: int) -> str:
    """Extract quotable moments."""
    prompt = f"""Extract the most quotable moments from this content.

Style: {style}
Count: {count}

Rules:
- Each quote should stand alone
- Memorable and shareable
- Trim unnecessary words
- Can slightly paraphrase for clarity
- Include attribution context if speaker mentioned

Content:
{content[:8000]}

Output as numbered quotes:"""

    return call_claude(prompt)


def generate_hooks(content: str, style: str, count: int) -> str:
    """Generate attention-grabbing hooks."""
    prompt = f"""Generate {count} attention-grabbing hooks based on this content.

Hook style: {style}

Hook types to vary:
- Curiosity gap: "Here's what nobody tells you about..."
- Contrarian: "Popular opinion is wrong about..."
- Story: "In 2019, a small startup..."
- Stat: "87% of marketers don't know..."
- Question: "Have you ever wondered why..."

Content:
{content[:8000]}

Output {count} numbered hooks, each on its own line:"""

    return call_claude(prompt)


def generate_summary(content: str, style: str) -> str:
    """Generate executive summary."""
    prompt = f"""Create an executive summary of this content.

Style: {style}
Length: 200-300 words

Rules:
- Lead with the main insight
- Include 3-5 key takeaways
- Maintain the original voice
- End with implications/next steps

Content:
{content[:8000]}

Output the summary:"""

    return call_claude(prompt)


def generate_newsletter(content: str, style: str) -> str:
    """Generate newsletter-friendly version."""
    prompt = f"""Transform this content into a newsletter section.

Style: {style}
Length: 500-800 words

Rules:
- Engaging subject line suggestion
- Personal, conversational tone
- Scannable with headers/bullets
- Include one clear call to action
- Email-friendly formatting

Content:
{content[:8000]}

Output with subject line suggestion first, then content:"""

    return call_claude(prompt)


if __name__ == "__main__":
    cli()
