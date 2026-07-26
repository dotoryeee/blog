"""좌측 네비에 최근 글 목록을 넣고, 전체 글 목록 페이지를 생성한다.

on_files: blog/all.md 를 만들어 전체 목록을 담는다.
on_nav:   좌측 네비에 최근 글 N개를 링크로 끼워 넣는다.

글 객체(Page)를 네비에 그대로 재사용하면 부모 관계가 덮어써져 블로그 플러그인의
이전·다음 글 링크가 깨질 수 있다. 그래서 Link 객체로 넣는다.
링크 주소는 슬러그를 직접 계산하지 않고 mkdocs가 만든 File.url 을 그대로 쓴다.
draft: true 인 글은 양쪽 모두에서 뺀다.
"""

import os
import re

from mkdocs.structure.files import File
from mkdocs.structure.nav import Link, Section

SKIP = {"blog_template.md"}

# 좌측 네비에 노출할 최근 글 수. 0으로 두면 전체를 넣는다.
NAV_RECENT = 30
NAV_TITLE = "최근 글"


def _read(path):
    with open(path, encoding="utf-8") as fp:
        return fp.read()


def _meta(text):
    head = re.match(r"---\n(.*?)\n---", text, re.S)
    if not head:
        return None
    meta = head.group(1)
    if re.search(r"^draft:\s*true", meta, re.M):
        return None
    date = re.search(r"^date:\s*(\d{4})-(\d{2})-(\d{2})", meta, re.M)
    title = re.search(r"^#\s+(.+)$", text, re.M)
    if not (date and title):
        return None
    cat = re.search(r"^categories:\s*\n\s*-\s*(.+)$", meta, re.M)
    return {
        "date": "-".join(date.groups()),
        "title": title.group(1).strip(),
        "cat": cat.group(1).strip() if cat else "",
    }


def _collect(docs_dir):
    root = os.path.join(docs_dir, "blog", "posts")
    posts = []
    for dirpath, _, names in os.walk(root):
        for name in sorted(names):
            if not name.endswith(".md") or name in SKIP:
                continue
            path = os.path.join(dirpath, name)
            info = _meta(_read(path))
            if not info:
                continue
            info["rel"] = os.path.relpath(
                path, os.path.join(docs_dir, "blog")
            ).replace(os.sep, "/")
            info["src"] = os.path.relpath(path, docs_dir).replace(os.sep, "/")
            posts.append(info)
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
    config._all_posts = posts
    files.append(File.generated(config, "blog/all.md", content=_render(posts)))
    return files


def on_nav(nav, config, files):
    posts = getattr(config, "_all_posts", None) or _collect(config.docs_dir)
    picked = posts if NAV_RECENT <= 0 else posts[:NAV_RECENT]

    # src_uri 로 File 을 찾아 mkdocs 가 계산한 url 을 그대로 쓴다
    by_src = {f.src_uri: f for f in files}
    items = []
    for p in picked:
        f = by_src.get(p["src"])
        if f is None:
            continue
        items.append(Link(p["title"], f.url))
    if not items:
        return nav

    section = Section(NAV_TITLE, items)
    nav.items.append(section)
    return nav
