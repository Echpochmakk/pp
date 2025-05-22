import requests
import json
import os
import argparse
from urllib.parse import urlparse

def fetch_releases(repo_url: str) -> list:
    path_parts = urlparse(repo_url).path.strip('/').split('/')
    if len(path_parts) != 2:
        raise ValueError("Невалидный URL. Пример: https://github.com/org/repo")

    owner, repo = path_parts
    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    response = requests.get(api_url)
    response.raise_for_status()
    releases = response.json()

    parsed = []
    for r in releases:
        parsed.append({
            "tag_name": r.get("tag_name"),
            "name": r.get("name"),
            "published_at": r.get("published_at"),
            "body": r.get("body"),
            "html_url": r.get("html_url")
        })

    return parsed

def save_to_json(data: list, path: str = "data/releases.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            existing = json.load(f)
    else:
        existing = []

    tags = {r['tag_name'] for r in existing}
    updated = existing + [r for r in data if r['tag_name'] not in tags]

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(updated, f, indent=2, ensure_ascii=False)

def get_latest_release(repo_url: str) -> dict:
    releases = fetch_releases(repo_url)
    return releases[0] if releases else {}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GitHub Release Parser")
    parser.add_argument("--url", required=True, help="Ссылка на репозиторий GitHub")
    args = parser.parse_args()
    rels = fetch_releases(args.url)
    save_to_json(rels)
    print(f"Сохранено {len(rels)} релизов.")
