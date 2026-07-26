"""전체 글 목록 페이지를 빌드 시점에 생성한다.

docs/blog/posts 아래의 글을 날짜 최신순으로 모아 blog/all.md 를 만든다.
링크는 슬러그를 직접 계산하지 않고 원본 .md 경로로 건다. mkdocs가 블로그
플러그인의 URL 규칙에 맞춰 알아서 바꿔주므로 규칙이 바뀌어도 깨지지 않는다.
draft: true 인 글은 목록에서 뺀다.
"""

import os
import re

from mkdocs.structure.files import File

SKIP = {"blog_template.md"}


def _collect(docs_dir):
    root = os.path.join(docs_dir, "blog", "posts")
    posts = []
    for dirpath, _, names in os.walk(root):
        for name in sorted(names):
            if not name.endswith(".md") or name in SKIP:
                continue
            path = os.path.join(dirpath, name)
            with open(path, encoding="utf-8") as fp:
                text = fp.read()
            head = re.match(r"---\n(.*?)\n---", text, re.S)
            if not head:
                continue
            meta = head.group(1)
            if re.search(r"^draft:\s*true", meta, re.M):
                continue
            date = re.search(r"^date:\s*(\d{4})-(\d{2})-(\d{2})", meta, re.M)
            title = re.search(r"^#\s+(.+)$", text, re.M)
            if not (date and title):
                continue
            cat = re.search(r"^categories:\s*\n\s*-\s*(.+)$", meta, re.M)
            rel = os.path.relpath(path, os.path.join(docs_dir, "blog"))
            posts.append(
                {
                    "date": "-".join(date.groups()),
                    "title": title.group(1).strip(),
                    "cat": cat.group(1).strip() if cat else "",
                    "rel": rel.replace(os.sep, "/"),
                }
            )
    posts.sort(key=lambda p: (p["date"], p["title"]), reverse=True)
    return posts


def _render(posts):
    lines = [
        "---",
        "hide:",
        "  - toc",
        "---",
        "# 전체 글",
        "",
        f"총 {len(posts)}편. 최신순.",
        "",
        "| 날짜 | 카테고리 | 제목 |",
        "|------|---------|------|",
    ]
    for p in posts:
        lines.append(f'| {p["date"]} | {p["cat"]} | [{p["title"]}]({p["rel"]}) |')
    lines.append("")
    return "\n".join(lines)


def on_files(files, config):
    posts = _collect(config.docs_dir)
    files.append(
        File.generated(config, "blog/all.md", content=_render(posts))
    )
    return files
