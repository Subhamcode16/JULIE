import unittest

from core.security import classify_zone, SecurityZone


class SecurityTestCase(unittest.TestCase):
    def test_green_action(self):
        self.assertEqual(classify_zone("open_application_action"), SecurityZone.GREEN)

    def test_yellow_action(self):
        self.assertEqual(classify_zone("write_file_action"), SecurityZone.YELLOW)

    def test_red_action(self):
        self.assertEqual(classify_zone("modify_registry_action"), SecurityZone.RED)


if __name__ == "__main__":
    unittest.main()
