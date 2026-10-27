import copy
import json
import unittest
from pathlib import Path

import catalog


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builtin = json.loads((Path(__file__).parents[1] / "entries/mingoyung.awakening.json").read_text(encoding="utf-8"))

    def video(self):
        item = copy.deepcopy(self.builtin)
        item.update(id="creator.example", title="Example", kind="video", durationSeconds=20,
                    asset={"url": "https://github.com/creator/animation/releases/download/v1/intro.mp4",
                           "format": "mp4", "bytes": 1024, "sha256": "a" * 64})
        return item

    def rejects(self, item):
        with self.assertRaises(catalog.Invalid):
            catalog.validate_entry(item)

    def test_builtin(self):
        self.assertEqual(catalog.validate_entry(self.builtin)["id"], catalog.BUILTIN)

    def test_valid_video_and_webm(self):
        self.assertEqual(catalog.validate_entry(self.video())["kind"], "video")
        item = self.video(); item["asset"].update(format="webm", url="https://raw.githubusercontent.com/c/r/v1/intro.webm")
        catalog.validate_entry(item)

    def test_reserved_builtin_id(self):
        item = self.video(); item["id"] = catalog.BUILTIN; self.rejects(item)
        item = copy.deepcopy(self.builtin); item["id"] = "other.builtin"; self.rejects(item)

    def test_builtin_cannot_download(self):
        item = copy.deepcopy(self.builtin); item["asset"] = self.video()["asset"]; self.rejects(item)

    def test_plain_strings_and_limits(self):
        for field in ("title", "author", "description"):
            with self.subTest(field=field):
                item = self.video(); item[field] = "x\n<script>"; self.rejects(item)
                item[field] = "x" * (257 if field == "description" else 81); self.rejects(item)

    def test_bad_ids(self):
        for ident in ("../outside", "Upper.Case", "bad/name", "..", "x" * 81):
            with self.subTest(ident=ident):
                item = self.video(); item["id"] = ident; self.rejects(item)

    def test_duration_limits(self):
        for duration in (0, 46, True, float("nan"), "20"):
            with self.subTest(duration=duration):
                item = self.video(); item["durationSeconds"] = duration; self.rejects(item)

    def test_disallowed_urls(self):
        for url in ("http://github.com/a/b", "https://github.com.evil.invalid/a.mp4", "https://127.0.0.1/a.mp4",
                    "https://user:secret@github.com/a.mp4", "https://github.com:444/a.mp4",
                    "https://github.com/a.mp4#fragment", "https://github.com/a.mp4#", "https://github.com/a b.mp4"):
            with self.subTest(url=url):
                item = self.video(); item["asset"]["url"] = url; self.rejects(item)

    def test_explicit_https_port(self):
        self.assertTrue(catalog.github_url("https://github.com:443/a/b", "source"))

    def test_cdn_redirect_has_no_extension_requirement(self):
        self.assertTrue(catalog.github_url("https://release-assets.githubusercontent.com/github-production-release-asset/uuid?sig=a", "redirect"))

    def test_initial_asset_extension(self):
        item = self.video(); item["asset"]["url"] = "https://github.com/a/b/intro.exe"; self.rejects(item)

    def test_media_size_and_digest(self):
        for size in (0, True, 125829121, 1.5, "1024"):
            item = self.video(); item["asset"]["bytes"] = size; self.rejects(item)
        for digest in ("a" * 63, "G" * 64, "A" * 64):
            item = self.video(); item["asset"]["sha256"] = digest; self.rejects(item)

    def test_supported_licenses(self):
        for license_id in catalog.LICENSES:
            item = self.video(); item["license"] = license_id; catalog.validate_entry(item)
        item["license"] = "local-only"; self.rejects(item)

    def test_no_script_fields(self):
        item = self.video(); item["script"] = "run.sh"; self.rejects(item)

    def test_filename_matches_id(self):
        with self.assertRaises(catalog.Invalid):
            catalog.validate_entry(self.video(), "different.json")

    def test_unique_catalog_ids(self):
        with self.assertRaises(catalog.Invalid):
            catalog.catalog_for([self.video(), self.video()])

    def test_entry_count_limit(self):
        with self.assertRaises(catalog.Invalid):
            catalog.catalog_for([self.video()] * 129)

    def test_duplicate_json_keys(self):
        with self.assertRaises(catalog.Invalid):
            catalog.parse(b'{"id":"first","id":"second"}', "duplicate")

    def test_unknown_and_missing_fields(self):
        item = self.video(); del item["licenseUrl"]; self.rejects(item)
        item = self.video(); item["asset"]["code"] = "unsafe"; self.rejects(item)

    def test_stable_generation(self):
        a, b = self.video(), copy.deepcopy(self.video()); b["id"] = "another.animation"
        self.assertEqual(catalog.encode(catalog.catalog_for([a, b])), catalog.encode(catalog.catalog_for([b, a])))


if __name__ == "__main__":
    unittest.main()
