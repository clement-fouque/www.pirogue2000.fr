import tempfile
import unittest
from pathlib import Path

from scripts.check_site import NOTICE_ROUTES, Page, resolve, validate

PAGES_URL = "https://clement-fouque.github.io/www.pirogue2000.fr/"


class SiteChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write("index.html", '<html lang="fr"><h1>Accueil</h1></html>')

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    def test_valid_site(self):
        self.assertEqual(validate(self.root), [])

    def test_empty_build_fails(self):
        self.assertTrue(validate(self.root / "missing"))

    def test_encoded_accent_and_directory_redirect_target(self):
        self.write("actions/santé/index.html", '<html lang="fr"><h1>Santé</h1><p id="soins">Soins</p></html>')
        self.write("index.html", '<html lang="fr"><h1>Accueil</h1><a href="/actions/sant%C3%A9/#soins">Santé</a></html>')
        self.assertEqual(validate(self.root), [])
        target, _ = resolve(self.root, "/", "/actions/sant%C3%A9")
        self.assertEqual(target, self.root / "actions/santé/index.html")

    def test_missing_link_and_anchor(self):
        self.write("index.html", '<html lang="fr"><h1>Accueil</h1><a href="/absent/">Lien</a><a href="#absent">Ancre</a></html>')
        errors = validate(self.root)
        self.assertTrue(any("missing internal target" in e for e in errors))
        self.assertTrue(any("missing anchor" in e for e in errors))

    def test_external_links_allowed_but_remote_runtime_rejected(self):
        self.write("index.html", '<html lang="fr"><h1>Accueil</h1><a href="https://facebook.com/example">Facebook</a><img alt="Photo" src="https://example.com/photo.jpg"></html>')
        self.assertEqual(len(validate(self.root)), 1)
        self.assertIn("remote runtime", validate(self.root)[0])

    def test_platform_link_rejected(self):
        self.write("index.html", '<html lang="fr"><h1>Accueil</h1><a href="https://a.jimdo.com/login">Login</a></html>')
        self.assertTrue(any("platform dependency" in e for e in validate(self.root)))

    def test_missing_css_asset_rejected(self):
        self.write("css/site.css", 'body{background:url("../images/missing.png")}')
        self.assertTrue(any("CSS asset" in e for e in validate(self.root)))

    def test_relative_css_asset(self):
        self.write("css/site.css", '@font-face{src:url("../fonts/font.ttf")}')
        self.write("fonts/font.ttf", "test fixture")
        self.assertEqual(validate(self.root), [])

    def test_nested_image_link_rejected(self):
        page = Page('<a href="/actions/"><a href="/photo.jpg"><img src="/photo.jpg" alt="Photo"></a></a>')
        self.assertIn("nested anchors", page.issues)

    def test_srcset_is_checked(self):
        page = Page('<img src="/small.jpg" srcset="/small.jpg 320w, /large.jpg 640w" alt="Photo">')
        self.assertIn(("/large.jpg", True), page.references)

    def test_form_inline_script_and_missing_alt_rejected(self):
        page = Page('<form></form><script>alert(1)</script><img src="/photo.jpg">')
        self.assertEqual(len(page.issues), 3)

    def test_duplicate_anchor_rejected(self):
        self.assertTrue(Page('<p id="same"></p><p id="same"></p>').issues)

    def test_image_omitted_from_migrated_page_rejected(self):
        inventory = {"pages": [{"route": "/", "images": ["/images/lost.jpg"]}], "assets": []}
        self.assertTrue(any("omitted source image" in e for e in validate(self.root, inventory)))

    def test_project_path_assets_and_navigation(self):
        prefix = "/www.pirogue2000.fr/"
        self.write("index.html", f'''<html lang="fr"><h1>Accueil</h1>
            <link rel="canonical" href="{PAGES_URL}">
            <link rel="stylesheet" href="{prefix}css/site.css">
            <script src="{prefix}js/site.js"></script>
            <a href="{prefix}actions/sant%C3%A9/?view=all#soins">Santé</a>
            <a href="{prefix}documents/report.pdf">PDF</a>
            <a href="{prefix}images/photo.jpg"><img alt="Photo"
              src="{prefix}images/small.webp"
              srcset="{prefix}images/small.webp 320w, {prefix}images/photo.jpg 640w"></a>
            </html>''')
        self.write("actions/santé/index.html", '''<html lang="fr"><h1 id="soins">Santé</h1>
            <a href="../../?home=1">Accueil</a><a href="#soins">Soins</a>
            <a href="mailto:example@example.com">Email</a><a href="tel:+33123456789">Téléphone</a>
            <a href="//example.com/">Externe</a></html>''')
        self.write("css/site.css", '@font-face{src:url("../fonts/font.ttf")}body{background:url("../images/photo.jpg")}')
        for path in ("fonts/font.ttf", "js/site.js", "documents/report.pdf",
                     "images/photo.jpg", "images/small.webp"):
            self.write(path, "fixture")
        self.assertEqual(validate(self.root, base_url=PAGES_URL), [])

    def test_project_path_rejects_unprefixed_stylesheet(self):
        self.write("css/site.css", "body{}")
        self.write("index.html", '<html lang="fr"><h1>Accueil</h1><link rel="stylesheet" href="/css/site.css"></html>')
        self.assertTrue(any("outside deployment path" in e for e in validate(self.root, base_url=PAGES_URL)))

    def test_project_path_rejects_links_escaping_prefix(self):
        for reference in ("/contact/", "/www.pirogue2000.fr-other/contact/",
                          "../contact/", "https://clement-fouque.github.io/contact/"):
            with self.subTest(reference=reference):
                self.write("contact/index.html", '<html lang="fr"><h1>Contact</h1></html>')
                self.write("index.html", f'<html lang="fr"><h1>Accueil</h1><a href="{reference}">Contact</a></html>')
                self.assertTrue(any("outside deployment path" in e for e in validate(self.root, base_url=PAGES_URL)))

    def test_project_path_rejects_css_escaping_prefix(self):
        self.write("images/photo.jpg", "fixture")
        self.write("css/site.css", 'body{background:url("/images/photo.jpg")}')
        self.assertTrue(any("outside deployment path" in e for e in validate(self.root, base_url=PAGES_URL)))

    def test_project_path_resolves_accented_route(self):
        self.write("actions/santé/index.html", '<html lang="fr"><h1>Santé</h1></html>')
        target, _ = resolve(self.root, "/www.pirogue2000.fr/", "/www.pirogue2000.fr/actions/sant%C3%A9/", PAGES_URL)
        self.assertEqual(target, self.root / "actions/santé/index.html")

    def test_project_path_preserves_inventory_checks(self):
        self.write("index.html", '<html lang="fr"><h1>Accueil</h1><img alt="Photo" src="/www.pirogue2000.fr/images/photo.jpg"></html>')
        self.write("images/photo.jpg", "fixture")
        for route in NOTICE_ROUTES:
            self.write(route.strip("/") + "/index.html", '<html lang="fr"><h1>Notice</h1></html>')
        self.write("CNAME", "www.pirogue2000.fr")
        self.write(".nojekyll", "")
        self.write("sitemap.xml", "<urlset/>")
        inventory = {"pages": [{"route": "/", "images": ["/images/photo.jpg"]}], "assets": []}
        self.assertEqual(validate(self.root, inventory, base_url=PAGES_URL), [])
        inventory["pages"][0]["images"] = ["/images/lost.jpg"]
        self.assertTrue(any("omitted source image" in e for e in validate(self.root, inventory, base_url=PAGES_URL)))


if __name__ == "__main__":
    unittest.main()
