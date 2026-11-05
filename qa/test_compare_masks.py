"""Synthetic verification for the silhouette evaluator; no Blender required."""
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from compare_masks import read_mask, score, overlay


class MaskComparisonTests(unittest.TestCase):
    def test_identical_masks_have_perfect_iou(self):
        mask = np.zeros((40, 50), dtype=bool)
        mask[10:30, 7:37] = True
        result = score(mask, mask.copy())
        self.assertEqual(result["iou"], 1.0)
        self.assertEqual(result["reference_coverage"], 1.0)
        self.assertEqual(result["centroid_offset_px_xy"], [0.0, 0.0])

    def test_shifted_mask_is_penalized(self):
        a = np.zeros((40, 50), dtype=bool)
        b = np.zeros((40, 50), dtype=bool)
        a[5:25, 5:25] = True
        b[5:25, 10:30] = True
        result = score(a, b)
        self.assertAlmostEqual(result["iou"], 300 / 500, places=6)
        self.assertEqual(result["centroid_offset_px_xy"], [5.0, 0.0])

    def test_empty_and_mismatched_are_rejected(self):
        a = np.ones((5, 5), dtype=bool)
        with self.assertRaises(ValueError):
            score(a, np.ones((6, 5), dtype=bool))
        with self.assertRaises(ValueError):
            score(a, np.zeros((5, 5), dtype=bool))

    def test_alpha_and_bright_on_dark_masks(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)
            alpha_image = np.zeros((8, 8, 4), dtype=np.uint8)
            alpha_image[2:6, 2:6] = [0, 0, 0, 255]
            Image.fromarray(alpha_image, "RGBA").save(p / "alpha.png")
            self.assertEqual(int(read_mask(p / "alpha.png").sum()), 16)
            image = np.zeros((8, 8), dtype=np.uint8)
            image[1:4, 2:7] = 255
            Image.fromarray(image, "L").save(p / "white.png")
            self.assertEqual(int(read_mask(p / "white.png").sum()), 15)
            self.assertEqual(int(read_mask(p / "white.png", invert=True).sum()), 49)

    def test_overlay_distinguishes_error_types(self):
        a = np.zeros((2, 2), dtype=bool)
        b = np.zeros((2, 2), dtype=bool)
        a[0, 0] = True
        a[0, 1] = True
        b[0, 0] = True
        b[1, 0] = True
        out = np.asarray(overlay(a, b))
        self.assertEqual(out[0, 0].tolist(), [65, 73, 82])
        self.assertEqual(out[0, 1].tolist(), [225, 65, 60])
        self.assertEqual(out[1, 0].tolist(), [40, 110, 225])


if __name__ == "__main__":
    unittest.main()
