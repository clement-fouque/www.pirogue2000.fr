import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote

from scripts.check_site import Page, validate


@unittest.skipUnless(shutil.which("hugo"), "Hugo is required for render-hook integration tests")
class HugoURLChecks(unittest.TestCase):
    def test_root_and_project_path_builds(self):
        repository = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            content = root / "content"
            shutil.copytree(repository / "content", content)
            for prefix in ("/", "/www.pirogue2000.fr/"):
                with self.subTest(prefix=prefix):
                    base_url = "https://example.org" + prefix
                    (content / "url-check.md").write_text(f'''---
title: URL checks
---
[Contact](/contact/?from=test#contenu)

[Already prefixed]({prefix}contact/)

[Relative](../contact/)

[Fragment](#contenu)

[External](https://example.com/contact/)

[Protocol relative](//example.com/contact/)

[Email](mailto:example@example.com)

[Phone](tel:+33123456789)

[![Linked photo](/images/i77db7029a535daeb.jpg)](/actions/)

![Photo](/images/i77db7029a535daeb.jpg)
''')
                    output = root / "public"
                    result = subprocess.run(
                        ["hugo", "--baseURL", base_url, "--contentDir", str(content),
                         "--destination", str(output), "--cleanDestinationDir", "--panicOnWarning"],
                        cwd=repository, capture_output=True, text=True,
                    )
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertEqual(validate(output, base_url=base_url), [])
                    page = Page((output / "url-check/index.html").read_text())
                    references = {unquote(reference) for reference, _ in page.references}
                    for expected in (
                        prefix + "contact/?from=test#contenu", prefix + "contact/",
                        "../contact/", "#contenu", "https://example.com/contact/",
                        "//example.com/contact/", "mailto:example@example.com", "tel:+33123456789",
                        prefix + "images/i77db7029a535daeb.jpg", prefix + "actions/",
                    ):
                        self.assertIn(expected, references)
                    self.assertNotIn("nested anchors", page.issues)
                    for image in page.images:
                        self.assertTrue(image["src"].startswith(prefix))
                        for item in image.get("srcset", "").split(","):
                            if item.strip():
                                self.assertTrue(item.strip().split()[0].startswith(prefix))


if __name__ == "__main__":
    unittest.main()
