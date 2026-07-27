from types import SimpleNamespace
import unittest

from cogs.management import ManagementCommand
from main import bot


class TemplateConfigurationTests(unittest.TestCase):
    def test_discovers_expected_extensions(self) -> None:
        names = bot.discover_extension_names()

        self.assertIn("basic", names)
        self.assertIn("management", names)
        self.assertNotIn("__init__", names)

    def test_extension_path_uses_discovered_allowlist(self) -> None:
        self.assertEqual(bot.extension_path("basic"), "cogs.basic")
        self.assertIsNone(bot.extension_path("../main"))
        self.assertIsNone(bot.extension_path("missing"))

    def test_privileged_intents_are_minimized(self) -> None:
        self.assertTrue(bot.intents.message_content)
        self.assertFalse(bot.intents.members)

    def test_direct_messages_do_not_receive_admin_access(self) -> None:
        interaction = SimpleNamespace(guild=None, user=object())

        self.assertFalse(ManagementCommand._is_admin(interaction))


if __name__ == "__main__":
    unittest.main()
