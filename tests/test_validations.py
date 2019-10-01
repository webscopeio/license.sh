import unittest

from license_sh.helpers import is_license_problem


class LicenseValidationsTestCase(unittest.TestCase):

  def test_simple_validation_test(self):
    whitelist = ['MIT', 'Apache-2.0']
    self.assertFalse(is_license_problem('MIT', whitelist), "MIT should not be not problematic, it's in a whitelist")

  def test_license_in_comma_separated_expression(self):
    whitelist = ['MIT', 'Apache-2.0']
    self.assertFalse(is_license_problem('MIT, Apache 2.0', whitelist), "MIT should not be not problematic, it's in a whitelist")

if __name__ == '__main__':
  unittest.main()
