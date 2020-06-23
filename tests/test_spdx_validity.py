import unittest

from license_sh.normalizer import normalize, is_spdx_compliant


class TestSPDXCompliance(unittest.TestCase):
    def test_mit_is_spdx_compliant(self):
        license = "MIT"
        self.assertEqual(True, is_spdx_compliant(license))

    def test_mit_lowercase_is_spdx_compliant(self):
        license = "mit"
        self.assertEqual(False, is_spdx_compliant(license))


if __name__ == "__main__":
    unittest.main()
