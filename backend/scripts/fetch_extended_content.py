"""Pulls additional BNHS content beyond the Omeka collections API already in
`documents`: blog posts (WordPress REST API) and monthly newsletter PDFs
(downloaded + text-extracted). Idempotent -- safe to re-run.

Usage:
    cd backend
    source .venv/bin/activate
    python scripts/fetch_extended_content.py
"""

import re
import sys
import zlib
from html.parser import HTMLParser
from pathlib import Path

import httpx
from pypdf import PdfReader

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import get_settings  # noqa: E402
from supabase import create_client  # noqa: E402

BLOG_API = "https://blog.bnhs.org/wp-json/wp/v2/posts"
NEWSLETTER_PAGE = "https://www.bnhs.org/news-letter"


class _HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data):
        self.parts.append(data)


def strip_html(html: str) -> str:
    stripper = _HTMLStripper()
    stripper.feed(html)
    text = "".join(stripper.parts)
    return re.sub(r"\s+", " ", text).strip()


def stable_id(text: str) -> int:
    return zlib.crc32(text.encode("utf-8"))


def fetch_blog_posts(supabase, client: httpx.Client) -> int:
    print("Fetching blog posts...")
    page = 1
    total_inserted = 0
    while True:
        response = client.get(BLOG_API, params={"per_page": 20, "page": page})
        if response.status_code == 400:
            break
        response.raise_for_status()
        posts = response.json()
        if not posts:
            break

        for post in posts:
            title = strip_html(post["title"]["rendered"])
            content = strip_html(post["content"]["rendered"])
            metadata = {
                "title": title,
                "content": content,
                "link": post["link"],
                "date": post["date"],
            }
            supabase.table("documents").upsert(
                {
                    "source_type": "blog_post",
                    "external_id": post["id"],
                    "title": title,
                    "source_file": post["link"],
                    "metadata": metadata,
                },
                on_conflict="source_type,external_id",
            ).execute()
            total_inserted += 1

        print(f"  page {page}: {len(posts)} posts")
        page += 1

    return total_inserted


def fetch_newsletters(supabase, client: httpx.Client) -> int:
    print("Fetching newsletter list...")
    response = client.get(NEWSLETTER_PAGE)
    response.raise_for_status()
    urls = sorted(set(re.findall(r'href="(https://www\.bnhs\.org/public/news_letter_pdf/[^"]+\.pdf)"', response.text)))
    print(f"  found {len(urls)} newsletter PDFs")

    total_inserted = 0
    for url in urls:
        filename = url.rsplit("/", 1)[-1]
        title = filename.replace(".pdf", "").replace("_", " ").replace("-", " ")
        external_id = stable_id(url)

        try:
            pdf_response = client.get(url, timeout=60)
            pdf_response.raise_for_status()
            reader = PdfReader(__import__("io").BytesIO(pdf_response.content))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            text = re.sub(r"\s+", " ", text).strip()
        except Exception as exc:
            print(f"  SKIP {filename}: {exc}")
            continue

        if not text:
            print(f"  SKIP {filename}: no extractable text (likely scanned images)")
            continue

        metadata = {"title": title, "content": text, "url": url, "page_count": len(reader.pages)}
        supabase.table("documents").upsert(
            {
                "source_type": "newsletter",
                "external_id": external_id,
                "title": title,
                "source_file": url,
                "metadata": metadata,
            },
            on_conflict="source_type,external_id",
        ).execute()
        total_inserted += 1
        print(f"  OK {filename} ({len(text)} chars)")

    return total_inserted


def main() -> None:
    settings = get_settings()
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)

    with httpx.Client(headers={"User-Agent": "codeforgood-bnhs-rag/1.0"}, follow_redirects=True) as client:
        blog_count = fetch_blog_posts(supabase, client)
        newsletter_count = fetch_newsletters(supabase, client)

    print(f"\nDone. blog_post: {blog_count}, newsletter: {newsletter_count}")


if __name__ == "__main__":
    main()
