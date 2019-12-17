import unittest

from license_sh.helpers import is_license_ok, normalize_license_expression

try:
    import license_sh_private

    private_package = True
except ImportError:
    private_package = False


class LicenseValidationsTestCase(unittest.TestCase):
    def test_simple_validation_test(self):
        whitelist = ["MIT", "Apache-2.0"]
        self.assertTrue(
            is_license_ok("MIT", whitelist),
            "MIT should not be not problematic, it's in a whitelist",
        )

    def test_license_in_comma_separated_expression(self):
        whitelist = ["MIT", "Apache-2.0"]
        # license.sh doesn't support commas, we support SPDX syntax
        self.assertEqual(is_license_ok("MIT, Apache 2.0", whitelist), False)

    def test_unparsable_expression(self):
        whitelist = ["MIT", "The Apache Software License, Version 2.0"]
        self.assertEqual(
            is_license_ok("The Apache Software License, Version 2.0", whitelist), True
        )

    def test_and_license_expression(self):
        whitelist = ["MIT", "Apache-2.0"]
        self.assertTrue(is_license_ok("(MIT AND Apache-2.0)", whitelist))
        self.assertFalse(is_license_ok("(MIT AND Apache-3.0)", whitelist))

    def test_or_license_expression(self):
        whitelist = ["MIT", "Apache-3.0"]
        self.assertTrue(is_license_ok("(MIT OR Apache-2.0)", whitelist))

    def test_complex_or_license_expression(self):
        whitelist = ["MIT", "Apache-3.0"]
        self.assertTrue(
            is_license_ok("((MIT and Apache-3.0) OR Apache-2.0)", whitelist)
        )
        self.assertTrue(
            is_license_ok("((License-2 or Apache-3.0) OR Apache-2.0)", whitelist)
        )
        self.assertFalse(
            is_license_ok("((License-2 and Apache-3.0) OR Apache-2.0)", whitelist)
        )

    def test_nested_invalid_expression_inside_complex_or_license_expression(self):
        whitelist = ["MIT", "Apache-3.0"]
        self.assertFalse(
            is_license_ok("((License-2, Apache-3.0) OR Apache-2.0)", whitelist)
        )

    def test_multi_operator_expression(self):
        whitelist = ["MIT"]
        self.assertEqual(
            is_license_ok("(BSD-2-Clause OR MIT OR Apache-2.0)", whitelist), True
        )

    @unittest.skipUnless(private_package, "requires license_sh_private package")
    def test_license_simple_expression_normalized(self):
        license_expression = "Apache-2"
        self.assertEqual("Apache-2.0", normalize_license_expression(license_expression))

    @unittest.skipUnless(private_package, "requires license_sh_private package")
    def test_license_complex_expression_normalized(self):
        license_expression = "(mit or Apache-2)"
        self.assertEqual(
            "(MIT OR Apache-2.0)", normalize_license_expression(license_expression)
        )


if __name__ == "__main__":
    unittest.main()
