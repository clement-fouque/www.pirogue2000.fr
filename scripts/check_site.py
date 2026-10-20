"""Validate Hugo output and the migrated source inventory, using only Python's stdlib."""
import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

ORIGIN = "https://www.pirogue2000.fr"
NOTICE_ROUTES = ["/about/", "/sitemap/", "/j/privacy/", "/j/legal-guarantee/", "/j/withdrawal/"]
PLATFORM_HOSTS = ("jimdo.com", "jimcdn.com", "jimstatic.com", "cloudflare.com")


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.references = []
        self.ids = set()
        self.images = []
        self.issues = []
        self.anchor_depth = 0
        self.h1_count = 0
        self.lang = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            if attrs["id"] in self.ids:
                self.issues.append(f"duplicate id: {attrs['id']}")
            self.ids.add(attrs["id"])
        if tag == "html":
            self.lang = attrs.get("lang")
        if tag == "h1":
            self.h1_count += 1
        if tag == "a":
            if self.anchor_depth:
                self.issues.append("nested anchors")
            self.anchor_depth += 1
        if tag in ("form", "iframe", "object", "embed"):
            self.issues.append(f"unexpected runtime element: {tag}")
        if tag == "script" and not attrs.get("src"):
            self.issues.append("unexpected inline script")
        if tag == "img":
            self.images.append(attrs)
            if not attrs.get("src"):
                self.issues.append("image without a source")
            if not attrs.get("alt"):
                self.issues.append(f"image without alternative text: {attrs.get('src')}")
        if tag in ("img", "script", "source", "video", "audio"):
            for attr in ("src", "poster"):
                if attrs.get(attr):
                    self.references.append((attrs[attr], True))
        if tag in ("a", "link") and attrs.get("href"):
            self.references.append((attrs["href"], tag == "link"))
        for item in attrs.get("srcset", "").split(","):
            if item.strip():
                self.references.append((item.strip().split()[0], True))
        for url in css_urls(attrs.get("style", "")):
            self.references.append((url, True))

    def handle_endtag(self, tag):
        if tag == "a":
            self.anchor_depth = max(0, self.anchor_depth - 1)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)


def css_urls(css):
    return re.findall(r"""url\(\s*['"]?([^'")\s]+)['"]?\s*\)""", css)


def resolve(root, current_url, reference):
    target = urlsplit(urljoin(ORIGIN + current_url, reference))
    if target.netloc and target.netloc != urlsplit(ORIGIN).netloc:
        return None, target
    path = unquote(target.path)
    local = root / path.lstrip("/")
    if path.endswith("/") or local.is_dir():
        local = local / "index.html"
    return local, target


def validate(root, inventory=None, source_root=None):
    root = Path(root).resolve()
    errors = []
    html_files = sorted(root.rglob("*.html"))
    if not html_files:
        return ["no generated HTML; run hugo first"]
    parsed = {path: Page(path.read_text()) for path in html_files}
    for path, page in parsed.items():
        relative = "/" + path.relative_to(root).as_posix()
        current = relative.removesuffix("index.html")
        errors.extend(f"{relative}: {issue}" for issue in page.issues)
        if page.lang != "fr":
            errors.append(f"{relative}: expected French document language")
        if page.h1_count != 1:
            errors.append(f"{relative}: expected one h1, found {page.h1_count}")
        for reference, runtime in page.references:
            target = urlsplit(reference)
            if target.scheme and target.scheme not in ("https", "http", "mailto", "tel"):
                errors.append(f"{relative}: unsupported URL: {reference}")
                continue
            if target.scheme in ("mailto", "tel"):
                continue
            if any(target.netloc == host or target.netloc.endswith("." + host) for host in PLATFORM_HOSTS):
                errors.append(f"{relative}: platform dependency: {reference}")
            local, target = resolve(root, current, reference)
            if local is None:
                if runtime:
                    errors.append(f"{relative}: remote runtime dependency: {reference}")
                continue
            if not local.is_relative_to(root) or not local.is_file():
                errors.append(f"{relative}: missing internal target: {reference}")
            elif target.fragment and local in parsed and unquote(target.fragment) not in parsed[local].ids:
                errors.append(f"{relative}: missing anchor: {reference}")
    for path in root.rglob("*.css"):
        relative = "/" + path.relative_to(root).as_posix()
        css = path.read_text()
        if "@import" in css:
            errors.append(f"{relative}: unexpected CSS import")
        for reference in css_urls(css):
            local, _ = resolve(root, relative, reference)
            if local is None or not local.is_relative_to(root) or not local.is_file():
                errors.append(f"{relative}: missing or remote CSS asset: {reference}")
    if inventory:
        for route in [p["route"] for p in inventory["pages"]] + NOTICE_ROUTES:
            local, _ = resolve(root, "/", route)
            if not local.is_file():
                errors.append(f"missing migrated route: {route}")
        for asset in inventory["assets"]:
            local = root / asset["local"].lstrip("/")
            if not local.is_file():
                errors.append(f"missing migrated asset: {asset['local']}")
            elif hashlib.sha256(local.read_bytes()).hexdigest() != asset["sha256"]:
                errors.append(f"changed migrated asset: {asset['local']}")
            if source_root and not (Path(source_root) / asset["local"].lstrip("/")).is_file():
                errors.append(f"missing repository asset: {asset['local']}")
        for page in inventory["pages"]:
            local, _ = resolve(root, "/", page["route"])
            if local not in parsed:
                continue
            refs = {unquote(urlsplit(ref).path) for ref, _ in parsed[local].references}
            for image in page["images"]:
                if image not in refs:
                    errors.append(f"{page['route']}: omitted source image: {image}")
        cname = root / "CNAME"
        if not cname.is_file() or cname.read_text().strip() != "www.pirogue2000.fr":
            errors.append("missing or incorrect CNAME")
        if not (root / ".nojekyll").is_file():
            errors.append("missing .nojekyll")
        if not (root / "sitemap.xml").is_file():
            errors.append("missing XML sitemap")
        pdfs = [a for a in inventory["assets"] if a["kind"] == "document"]
        for pdf in pdfs:
            path = root / pdf["local"].lstrip("/")
            if path.is_file() and not path.read_bytes().startswith(b"%PDF-"):
                errors.append(f"invalid PDF: {pdf['local']}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", nargs="?", default="public")
    args = parser.parse_args()
    inventory = json.loads(Path("docs/source-inventory.json").read_text())
    errors = validate(Path(args.directory), inventory, Path("static"))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    files = {asset["local"] for asset in inventory["assets"]}
    print(f"Site OK: {len(inventory['pages']) + len(NOTICE_ROUTES)} migrated routes, "
          f"{len(inventory['assets'])} source asset mappings ({len(files)} files), "
          "internal links and local runtime resources.")


if __name__ == "__main__":
    main()
