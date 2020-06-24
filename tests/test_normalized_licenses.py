import unittest

from license_sh.normalizer import normalize


class TestNormalizedLicenses(unittest.TestCase):
    def test_normalized_license_returned_self(self):
        license = "MIT"
        self.assertEqual(("MIT", False), normalize(license))

    def test_dot_o_license(self):
        license = "Apache-2.0"
        self.assertEqual(("Apache-2.0", False), normalize(license))

    def test_normalized_license(self):
        license = "Apache2"
        self.assertEqual(("Apache-2.0", True), normalize(license))

    def test_unknown_license(self):
        license = "Whatever very weird license"
        self.assertEqual((license, False), normalize(license))

    def test_lowercase_license(self):
        license = "mit"
        self.assertEqual(("MIT", True), normalize(license))

    def test_complex_license(self):
        license = "M AND I AND T"
        self.assertEqual(("MIT", True), normalize(license))

    def test_license_identified_by_long_name(self):
        license = "GNU Free Documentation License v1.1"
        self.assertEqual(("GFDL-1.1", True), normalize(license))

    # Not implemented yet
    @unittest.skip
    def test_license_identified_by_long_name_uppercase_problem(self):
        license = "ISC license"
        self.assertEqual(("ISC", True), normalize(license))

    @unittest.skip
    def test_license_with_space_instead_of_dash(self):
        license = "MPL 1.0"
        self.assertEqual(("MPL-1.0", True), normalize(license))


if __name__ == "__main__":
    unittest.main()
