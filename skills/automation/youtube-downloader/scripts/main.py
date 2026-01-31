#!/usr/bin/env python3
"""
YouTube Downloader - Download videos, audio, and transcripts.

Usage:
    python main.py download "https://youtube.com/watch?v=..."
    python main.py audio "https://youtube.com/watch?v=..." --format mp3
    python main.py transcript "https://youtube.com/watch?v=..."
    python main.py playlist "https://youtube.com/playlist?list=..."
"""

import click
from pathlib import Path
from typing import Optional
import subprocess
import json
import re


def check_ytdlp():
    """Check if yt-dlp is installed."""
    try:
        result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def sanitize_filename(title: str) -> str:
    """Convert title to safe filename."""
    # Remove invalid characters
    clean = re.sub(r'[<>:"/\\|?*]', '', title)
    # Replace spaces with hyphens
    clean = re.sub(r'\s+', '-', clean)
    # Limit length
    return clean[:100].lower()


def get_video_info(url: str) -> dict:
    """Get video metadata."""
    cmd = ['yt-dlp', '--dump-json', '--no-download', url]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return json.loads(result.stdout)
    return {}


@click.group()
def cli():
    """YouTube Downloader - Video, audio, and transcript extraction."""
    if not check_ytdlp():
        click.echo("Error: yt-dlp not installed")
        click.echo("Run: pip install yt-dlp")
        raise SystemExit(1)


@cli.command()
@click.argument('url')
@click.option('--format', '-f', 'video_format', default='mp4',
              type=click.Choice(['mp4', 'webm', 'mkv']))
@click.option('--quality', '-q', default='1080p',
              type=click.Choice(['best', '2160p', '1080p', '720p', '480p', '360p']))
@click.option('--output', '-o', type=click.Path(), help='Output file path')
def download(url: str, video_format: str, quality: str, output: Optional[str]):
    """Download video from YouTube."""
    click.echo("\n  YouTube Download")
    click.echo("  " + "=" * 40)
    click.echo(f"  URL: {url}")
    click.echo(f"  Format: {video_format}")
    click.echo(f"  Quality: {quality}")

    # Get info first
    click.echo("  Fetching video info...")
    info = get_video_info(url)
    title = info.get('title', 'video')
    duration = info.get('duration', 0)
    click.echo(f"  Title: {title}")
    click.echo(f"  Duration: {duration // 60}:{duration % 60:02d}")

    # Determine output path
    if output:
        output_path = output
    else:
        output_path = f"{sanitize_filename(title)}.{video_format}"

    # Build yt-dlp command
    if quality == 'best':
        format_str = f'bestvideo[ext={video_format}]+bestaudio/best[ext={video_format}]/best'
    else:
        height = quality.replace('p', '')
        format_str = f'bestvideo[height<={height}][ext={video_format}]+bestaudio/best[height<={height}]'

    cmd = [
        'yt-dlp',
        '-f', format_str,
        '--merge-output-format', video_format,
        '-o', output_path,
        url
    ]

    click.echo("  Downloading...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        click.echo("\n  " + "-" * 40)
        click.echo("  [Done] Downloaded successfully")
        click.echo(f"  Output: {output_path}")
    else:
        click.echo("  [Error] Download failed")
        click.echo(f"  {result.stderr[:200]}")


@cli.command()
@click.argument('url')
@click.option('--format', '-f', 'audio_format', default='mp3',
              type=click.Choice(['mp3', 'm4a', 'wav', 'opus', 'flac']))
@click.option('--quality', '-q', default='192',
              type=click.Choice(['64', '128', '192', '256', '320', 'best']))
@click.option('--output', '-o', type=click.Path(), help='Output file path')
def audio(url: str, audio_format: str, quality: str, output: Optional[str]):
    """Extract audio from YouTube video."""
    click.echo("\n  Audio Extraction")
    click.echo("  " + "=" * 40)
    click.echo(f"  URL: {url}")
    click.echo(f"  Format: {audio_format}")
    click.echo(f"  Quality: {quality}kbps")

    # Get info
    click.echo("  Fetching video info...")
    info = get_video_info(url)
    title = info.get('title', 'audio')
    click.echo(f"  Title: {title}")

    # Output path
    if output:
        output_path = output
    else:
        output_path = f"{sanitize_filename(title)}.{audio_format}"

    # Build command
    cmd = [
        'yt-dlp',
        '-x',  # Extract audio
        '--audio-format', audio_format,
        '-o', output_path.replace(f'.{audio_format}', '.%(ext)s'),
        url
    ]

    if quality != 'best':
        cmd.extend(['--audio-quality', f'{quality}k'])

    click.echo("  Extracting audio...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        click.echo("\n  " + "-" * 40)
        click.echo("  [Done] Audio extracted")
        click.echo(f"  Output: {output_path}")
    else:
        click.echo("  [Error] Extraction failed")


@cli.command()
@click.argument('url')
@click.option('--translate', '-t', help='Translate to language code (e.g., en)')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
def transcript(url: str, translate: Optional[str], output: Optional[str]):
    """Download transcript/subtitles from YouTube."""
    click.echo("\n  Transcript Download")
    click.echo("  " + "=" * 40)
    click.echo(f"  URL: {url}")

    # Get info
    click.echo("  Fetching video info...")
    info = get_video_info(url)
    title = info.get('title', 'transcript')
    click.echo(f"  Title: {title}")

    # Output path
    if output:
        output_base = output
    else:
        output_base = sanitize_filename(title)

    # Try to get auto-generated or manual subtitles
    cmd = [
        'yt-dlp',
        '--write-auto-sub' if not translate else '--write-sub',
        '--sub-format', 'srt',
        '--skip-download',
        '-o', output_base,
        url
    ]

    if translate:
        cmd.extend(['--sub-lang', translate])

    click.echo("  Downloading subtitles...")
    subprocess.run(cmd, capture_output=True, text=True)

    # Find the subtitle file
    subtitle_files = list(Path('.').glob(f'{output_base}*.srt')) + \
                     list(Path('.').glob(f'{output_base}*.vtt'))

    if subtitle_files:
        # Convert SRT to plain text
        srt_path = subtitle_files[0]
        txt_path = Path(f"{output_base}.txt")

        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove timestamps and numbers
        lines = content.split('\n')
        text_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.isdigit():
                continue
            if '-->' in line:
                continue
            text_lines.append(line)

        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(' '.join(text_lines))

        click.echo("\n  " + "-" * 40)
        click.echo("  [Done] Transcript saved")
        click.echo(f"  SRT: {srt_path}")
        click.echo(f"  TXT: {txt_path}")
    else:
        click.echo("  [Warning] No subtitles available")
        click.echo("  Tip: Use whisper-transcription to generate from audio")


@cli.command()
@click.argument('url')
@click.option('--limit', '-l', type=int, help='Maximum videos to download')
@click.option('--audio-only', '-a', is_flag=True, help='Download audio only')
@click.option('--output', '-o', type=click.Path(), help='Output directory')
def playlist(url: str, limit: Optional[int], audio_only: bool, output: Optional[str]):
    """Download videos from a playlist."""
    click.echo("\n  Playlist Download")
    click.echo("  " + "=" * 40)
    click.echo(f"  URL: {url}")

    # Get playlist info
    cmd = ['yt-dlp', '--flat-playlist', '--dump-json', url]
    result = subprocess.run(cmd, capture_output=True, text=True)

    videos = [json.loads(line) for line in result.stdout.strip().split('\n') if line]
    total = len(videos)

    if limit:
        videos = videos[:limit]

    click.echo(f"  Videos: {len(videos)}/{total}")

    output_dir = Path(output) if output else Path('.')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Download each video
    for i, video in enumerate(videos, 1):
        video_url = f"https://youtube.com/watch?v={video['id']}"
        video_title = video.get('title', video['id'])
        click.echo(f"\n  [{i}/{len(videos)}] {video_title[:50]}...")

        output_template = str(output_dir / f"{i:02d}-%(title)s.%(ext)s")

        if audio_only:
            cmd = [
                'yt-dlp', '-x',
                '--audio-format', 'mp3',
                '-o', output_template,
                video_url
            ]
        else:
            cmd = [
                'yt-dlp',
                '-f', 'bestvideo[height<=1080]+bestaudio/best',
                '--merge-output-format', 'mp4',
                '-o', output_template,
                video_url
            ]

        subprocess.run(cmd, capture_output=True)
        click.echo("    Done")

    click.echo("\n  " + "-" * 40)
    click.echo(f"  [Done] Downloaded {len(videos)} videos")
    click.echo(f"  Output: {output_dir}")


@cli.command()
@click.argument('url')
@click.option('--format', '-f', 'output_format', default='text',
              type=click.Choice(['text', 'json']))
def info(url: str, output_format: str):
    """Get video metadata."""
    click.echo("\n  Video Information")
    click.echo("  " + "=" * 40)

    info = get_video_info(url)

    if not info:
        click.echo("  [Error] Could not fetch video info")
        return

    if output_format == 'json':
        click.echo(json.dumps(info, indent=2))
    else:
        click.echo(f"  Title: {info.get('title', 'N/A')}")
        click.echo(f"  Channel: {info.get('channel', 'N/A')}")
        click.echo(f"  Duration: {info.get('duration', 0) // 60}:{info.get('duration', 0) % 60:02d}")
        click.echo(f"  Views: {info.get('view_count', 0):,}")
        click.echo(f"  Likes: {info.get('like_count', 0):,}")
        click.echo(f"  Published: {info.get('upload_date', 'N/A')}")
        click.echo(f"  Description: {info.get('description', 'N/A')[:200]}...")

        if info.get('tags'):
            click.echo(f"  Tags: {', '.join(info['tags'][:10])}")


if __name__ == "__main__":
    cli()
