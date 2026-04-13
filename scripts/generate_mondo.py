#!/usr/bin/env python3
"""
Mondo Style Design Generator
Automatically generates Mondo-style prompts and creates images for posters, book covers, album art, etc.
"""

import os
import sys
import argparse
from datetime import datetime

from gemini_client import get_genai_client, iter_response_parts


DEFAULT_MODEL = 'gemini-2.5-flash-image'

def get_api_key():
    from gemini_client import get_gemini_api_key

    return get_gemini_api_key()

def generate_prompt(subject, design_type, style="auto"):
    """
    Generate Mondo-style prompt based on subject, type, and style

    Args:
        subject: The subject matter (e.g., "Blade Runner cyberpunk film", "Neuromancer novel")
        design_type: Type of design ("movie", "book", "album", "event")
        style: Visual style ("olly-moss", "tyler-stout", "minimal", "atmospheric", "auto")

    Returns:
        Generated prompt string
    """

    # Base Mondo aesthetic elements
    base_elements = "Mondo poster style, screen print aesthetic, limited edition poster art"

    # Style-specific modifiers (simplified to avoid clutter)
    style_modifiers = {
        "olly-moss": "ultra-minimal, 2-3 color screen print, single symbolic element, Olly Moss negative space approach",
        "tyler-stout": "intricate detailed composition, Tyler Stout style, character-focused",
        "minimal": "minimalist, centered single focal point, 2-3 color palette, clean simple composition",
        "atmospheric": "single strong focal element with atmospheric background, 3-4 color screen print, clean layered composition",
        "negative-space": "figure-ground inversion where negative space WITHIN silhouette reveals hidden element, clever dual imagery, Olly Moss style visual pun, 2-color duotone, what's missing tells the story"
    }

    # Type-specific templates (optimized for clarity and 9:16 vertical format)
    if design_type == "movie":
        if style == "auto" or style == "minimal":
            prompt = f"{subject} in {base_elements}, vertical 9:16 portrait format, centered single focal element, 3-color screen print, clean minimalist composition, symbolic not literal, halftone texture, vintage 1970s-80s aesthetic, simple and iconic"
        else:
            prompt = f"{subject} in {base_elements}, vertical 9:16 portrait format, {style_modifiers.get(style, style_modifiers['atmospheric'])}, vintage poster aesthetic, clean focused design"

    elif design_type == "book":
        if style == "auto" or style == "minimal":
            prompt = f"{subject} book cover in {base_elements}, vertical 9:16 portrait format, single symbolic centerpiece, 2-3 color palette, clean typography, minimalist literary design, simple focused composition, vintage book aesthetic"
        else:
            prompt = f"{subject} book cover in {base_elements}, vertical 9:16 format, {style_modifiers.get(style, style_modifiers['minimal'])}, clean focused design, vintage book aesthetic"

    elif design_type == "album":
        if style == "auto" or style == "minimal":
            prompt = f"{subject} album cover in {base_elements}, square 1:1 format, single bold central image, 3 color screen print, clean minimalist design, vintage vinyl aesthetic, simple iconic imagery"
        else:
            prompt = f"{subject} album cover in {base_elements}, square 1:1 format, {style_modifiers.get(style, style_modifiers['minimal'])}, vintage vinyl aesthetic, clean design"

    elif design_type == "event":
        if style == "auto":
            prompt = f"{subject} event poster in {base_elements}, vertical 9:16 format, single focal point, 3 color high contrast, clean bold design, vintage concert poster aesthetic, simple memorable composition"
        else:
            prompt = f"{subject} event poster in {base_elements}, vertical 9:16 format, {style_modifiers.get(style, style_modifiers['minimal'])}, clean vintage poster design"

    else:
        # Generic fallback
        prompt = f"{subject} in {base_elements}, {style_modifiers.get(style, style_modifiers['minimal'])}, vintage limited edition print aesthetic"

    return prompt

def generate_image(prompt, output_path=None, model=DEFAULT_MODEL, aspect_ratio="9:16"):
    """Generate an image with the official Gemini API."""
    get_api_key()
    client = get_genai_client()

    print(f"Generating image with model: {model}")
    print(f"Aspect ratio: {aspect_ratio}")
    print(f"Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
    print("Please wait...\n")

    try:
        from google.genai import types

        response = client.models.generate_content(
            model=model,
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"]
            ),
        )

        image_part = None
        for part in iter_response_parts(response):
            if part.inline_data is not None:
                image_part = part
                break

        if image_part is None:
            print("Error: No image data in response")
            return None

        if not output_path:
            timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            output_path = f"outputs/mondo-{timestamp}.png"

        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        image_part.as_image().save(output_path)
        print(f"✓ Image saved successfully to {output_path}")
        return output_path
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(
        description='Generate Mondo-style designs for posters, book covers, and album art',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a movie poster (default 9:16 vertical)
  python3 generate_mondo.py "Akira cyberpunk anime" movie

  # Generate a book cover with minimal style
  python3 generate_mondo.py "1984 dystopian novel" book --style minimal

  # Generate album art with square ratio
  python3 generate_mondo.py "Pink Floyd The Wall progressive rock" album --aspect-ratio 1:1

  # Generate horizontal poster
  python3 generate_mondo.py "Jazz Festival 2024" event --aspect-ratio 16:9

  # Generate with custom ratio
  python3 generate_mondo.py "Western film" movie --aspect-ratio 2:3 --style atmospheric

  # Only generate prompt without creating image
  python3 generate_mondo.py "Dune sci-fi epic" movie --no-generate
        """
    )

    parser.add_argument('subject', help='Subject matter (e.g., "Blade Runner cyberpunk film")')
    parser.add_argument('type', choices=['movie', 'book', 'album', 'event'],
                       help='Type of design to create')
    parser.add_argument('--style', choices=['auto', 'olly-moss', 'tyler-stout', 'minimal', 'atmospheric', 'negative-space'],
                       default='auto', help='Visual style approach (default: auto)')
    parser.add_argument('--aspect-ratio', '--ratio', dest='aspect_ratio', default='9:16',
                       help='Aspect ratio for the image (default: 9:16). Examples: 9:16, 16:9, 1:1, 2:3, 3:2')
    parser.add_argument('--output', help='Output file path (default: outputs/mondo-TIMESTAMP.png)')
    parser.add_argument('--model', default=DEFAULT_MODEL,
                       help=f'Model to use for generation (default: {DEFAULT_MODEL})')
    parser.add_argument('--no-generate', action='store_true',
                       help='Only generate prompt without creating image')

    args = parser.parse_args()

    # Generate prompt
    prompt = generate_prompt(args.subject, args.type, args.style)

    print("=" * 80)
    print("GENERATED MONDO-STYLE PROMPT")
    print("=" * 80)
    print(prompt)
    print("=" * 80)
    print()

    # Generate image if requested
    if not args.no_generate:
        output_path = generate_image(prompt, args.output, args.model, args.aspect_ratio)
        if output_path:
            print(f"\n✓ Success! Design saved to: {output_path}")
        else:
            print("\n✗ Failed to generate image")
            sys.exit(1)
    else:
        print("Prompt generation complete. Use --no-generate=false to create the image.")

if __name__ == '__main__':
    main()
