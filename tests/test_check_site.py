import tempfile
import unittest
from pathlib import Path

from scripts.check_site import Page, resolve, validate


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


if __name__ == "__main__":
    unittest.main()
