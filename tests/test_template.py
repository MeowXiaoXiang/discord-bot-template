from io import StringIO
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

from discord.ext import commands
from dotenv import dotenv_values

from cogs import management as management_module
from cogs.management import ManagementCommand
from main import DiscordBot, _reply_to_interaction_error, bot


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

    def test_empty_environment_value_with_comment_remains_empty(self) -> None:
        values = dotenv_values(stream=StringIO("MAINTAINER_ID= # optional\n"))

        self.assertEqual(values["MAINTAINER_ID"], "")


class InteractionErrorTests(unittest.IsolatedAsyncioTestCase):
    async def test_error_reply_uses_initial_response_or_followup(self) -> None:
        for responded in (False, True):
            with self.subTest(responded=responded):
                interaction = SimpleNamespace(
                    response=SimpleNamespace(
                        is_done=Mock(return_value=responded),
                        send_message=AsyncMock(),
                    ),
                    followup=SimpleNamespace(send=AsyncMock()),
                )
                await _reply_to_interaction_error(interaction, "command failed")
                if responded:
                    interaction.followup.send.assert_awaited_once_with(
                        "command failed", ephemeral=True
                    )
                    interaction.response.send_message.assert_not_awaited()
                else:
                    interaction.response.send_message.assert_awaited_once_with(
                        "command failed", ephemeral=True
                    )
                    interaction.followup.send.assert_not_awaited()


class ExtensionManagementTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.bot = SimpleNamespace(
            is_owner=AsyncMock(return_value=True),
            extension_path=bot.extension_path,
            management_extension=bot.management_extension,
            load_extension=AsyncMock(),
            unload_extension=AsyncMock(),
            reload_extension=AsyncMock(),
            tree=SimpleNamespace(sync=AsyncMock()),
        )
        self.cog = ManagementCommand(self.bot)
        self.interaction = SimpleNamespace(
            user=object(),
            response=SimpleNamespace(defer=AsyncMock()),
            edit_original_response=AsyncMock(),
        )

    async def test_non_owner_cannot_change_any_extensions(self) -> None:
        self.bot.is_owner.return_value = False
        for action in ("load", "unload", "reload"):
            await self.cog._extension_action(self.interaction, action, "basic")
        self.bot.load_extension.assert_not_awaited()
        self.bot.unload_extension.assert_not_awaited()
        self.bot.reload_extension.assert_not_awaited()
        self.bot.tree.sync.assert_not_awaited()

    async def test_successful_actions_acknowledge_then_mutate_then_sync(self) -> None:
        for action in ("load", "unload", "reload"):
            with self.subTest(action=action):
                events = []

                async def acknowledge(**kwargs):
                    events.append("defer")

                async def mutate(name):
                    events.append(name)

                async def sync():
                    events.append("sync")

                self.interaction.response.defer.side_effect = acknowledge
                getattr(self.bot, f"{action}_extension").side_effect = mutate
                self.bot.tree.sync.side_effect = sync
                await self.cog._extension_action(self.interaction, action, "basic")
                self.assertEqual(events, ["defer", "cogs.basic", "sync"])
                self.interaction.response.defer.assert_awaited_with(
                    ephemeral=True, thinking=True
                )
                embed = self.interaction.edit_original_response.call_args.kwargs["embed"]
                self.assertIn("已同步", embed.description)

    async def test_missing_extension_and_core_unload_do_not_mutate(self) -> None:
        await self.cog._extension_action(self.interaction, "load", "../main")
        await self.cog._extension_action(self.interaction, "unload", "management")
        self.bot.load_extension.assert_not_awaited()
        self.bot.unload_extension.assert_not_awaited()
        self.bot.tree.sync.assert_not_awaited()

    @patch.object(management_module, "logger")
    async def test_failed_actions_do_not_sync(self, mocked_logger) -> None:
        cases = (
            ("load", commands.ExtensionAlreadyLoaded("cogs.basic")),
            ("unload", commands.ExtensionNotLoaded("cogs.basic")),
            ("reload", RuntimeError("setup failed")),
        )
        for action, error in cases:
            with self.subTest(action=action):
                getattr(self.bot, f"{action}_extension").side_effect = error
                await self.cog._extension_action(self.interaction, action, "basic")
                self.bot.tree.sync.assert_not_awaited()
        mocked_logger.opt.assert_called()

    @patch.object(management_module, "logger")
    async def test_sync_failure_reports_that_extension_already_changed(
        self, mocked_logger
    ) -> None:
        self.bot.tree.sync.side_effect = RuntimeError("sync unavailable")
        await self.cog._extension_action(self.interaction, "load", "basic")
        self.bot.load_extension.assert_awaited_once_with("cogs.basic")
        embed = self.interaction.edit_original_response.call_args.kwargs["embed"]
        self.assertIn("已載入模組，但同步失敗", embed.title)
        self.assertIn("本機狀態已變更", embed.description)
        mocked_logger.opt.assert_called()

    async def test_example_extensions_register_commands_offline(self) -> None:
        async with DiscordBot() as instance:
            for name in instance.discover_extension_names():
                await instance.load_extension(instance.extension_path(name))
            self.assertIn("ping", instance.all_commands)
            self.assertIsNotNone(instance.tree.get_command("ping_slash"))
            self.assertIsNotNone(instance.tree.get_command("ping_hybrid"))
            self.assertIsNotNone(instance.tree.get_command("載入模組"))
            await instance.unload_extension("cogs.basic")
            self.assertIsNone(instance.tree.get_command("ping_slash"))


if __name__ == "__main__":
    unittest.main()
