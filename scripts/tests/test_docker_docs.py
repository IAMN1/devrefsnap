"""Verify each complete Docker listing against the source linked above it."""
import os
from pathlib import Path
import unittest

from markdown_it import MarkdownIt


ROOT = Path(__file__).resolve().parents[2]


class DockerListingTests(unittest.TestCase):
    def test_full_files_match_in_both_editions(self):
        listings = {
            "build-context.md": (
                "docker-build-context/main.py",
                "docker-build-context/.dockerignore",
                "docker-build-context/dockers/Dockerfile",
                "docker-build-context/compose.yaml",
                "docker-build-context/dockers/compose.yaml",
            ),
            "compose-file.md": ("docker-build-context/.dockerignore",),
            "lab.md": (
                "compose-site/Dockerfile",
                "compose-site/compose.yaml",
                "compose-site/gateway.conf",
            ),
        }
        parser = MarkdownIt()
        for language in ("ru", "en"):
            for page, filenames in listings.items():
                path = ROOT / "docs" / language / "tools/docker" / page
                tokens = parser.parse(path.read_text(encoding="utf-8"))
                linked_blocks = {}
                for index, block in enumerate(tokens):
                    if block.type != "fence" or index < 2:
                        continue
                    paragraph = tokens[index - 2]
                    if tokens[index - 1].type != "paragraph_close" or paragraph.type != "inline":
                        continue
                    for child in paragraph.children:
                        if child.type == "link_open":
                            linked_blocks.setdefault(child.attrGet("href"), []).append(block.content)
                for filename in filenames:
                    with self.subTest(language=language, page=page, source=filename):
                        source = ROOT / "examples/tools" / filename
                        link = Path(os.path.relpath(source, path.parent)).as_posix()
                        # Compare at the reader-visible link, even when two files have the same name.
                        blocks = linked_blocks.get(link, [])
                        self.assertEqual(len(blocks), 1, f"Expected one listing below {link}")
                        self.assertTrue(blocks[0] == source.read_text(encoding="utf-8"), f"Listing differs from {filename}")
