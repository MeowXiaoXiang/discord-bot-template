from __future__ import annotations

import os
import sys
import traceback
from datetime import UTC, datetime
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from loguru import logger

BASE_DIR = Path(__file__).resolve().parent
BOT_VERSION = "v1.1"
EMBED_DESCRIPTION_LIMIT = 4096
EMBED_FIELD_LIMIT = 1024


class CustomHelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping) -> None:
        embed = discord.Embed(
            title="指令總覽",
            description="以下是目前可用的指令列表",
            color=discord.Color.blue(),
        )
        for cog, commands_list in mapping.items():
            filtered = await self.filter_commands(commands_list, sort=True)
            if not filtered:
                continue

            name = cog.qualified_name if cog else "未分類"
            value = "\n".join(
                f"`{self.context.clean_prefix}{command.name}` - {command.short_doc}"
                for command in filtered
            )
            embed.add_field(name=name, value=value[:EMBED_FIELD_LIMIT], inline=False)

        embed.set_footer(
            text=f"輸入 {self.context.clean_prefix}help 指令名稱 查看詳細說明"
        )
        if self.context.me is not None:
            embed.set_author(
                name=self.context.me.name,
                icon_url=self.context.me.display_avatar.url,
            )
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command) -> None:
        embed = discord.Embed(
            title=f"指令說明：{command.name}",
            description=command.help or "（沒有詳細說明）",
            color=discord.Color.green(),
        )
        if command.usage:
            embed.add_field(
                name="用法",
                value=f"`{self.context.clean_prefix}{command.name} {command.usage}`",
                inline=False,
            )
        await self.get_destination().send(embed=embed)

    async def send_error_message(self, error) -> None:
        embed = discord.Embed(
            title="Help 指令錯誤",
            description=str(error)[:EMBED_DESCRIPTION_LIMIT],
            color=discord.Color.red(),
        )
        await self.get_destination().send(embed=embed)


class DiscordBot(commands.Bot):
    cogs_package = "cogs"
    cogs_directory = BASE_DIR / cogs_package
    management_name = "management"
    management_extension = f"{cogs_package}.{management_name}"

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            intents=intents,
            help_command=CustomHelpCommand(),
        )
        self.version = BOT_VERSION
        self.started_at = datetime.now(UTC)
        self.maintainer_id: int | None = None

    @classmethod
    def discover_extension_names(cls) -> tuple[str, ...]:
        """Return loadable top-level Cog module names in deterministic order."""
        return tuple(
            path.stem
            for path in sorted(
                cls.cogs_directory.glob("*.py"),
                key=lambda item: item.name.casefold(),
            )
            if path.stem != "__init__" and path.stem.isidentifier()
        )

    @classmethod
    def extension_path(cls, name: str) -> str | None:
        """Resolve a user-provided Cog name against the discovered allowlist."""
        normalized_name = name.strip()
        if normalized_name == "__init__" or not normalized_name.isidentifier():
            return None

        candidate = cls.cogs_directory / f"{normalized_name}.py"
        if not candidate.is_file():
            return None
        return f"{cls.cogs_package}.{normalized_name}"

    async def setup_hook(self) -> None:
        application = self.application or await self.application_info()

        configured_maintainer_id = os.getenv("MAINTAINER_ID", "").strip()
        if configured_maintainer_id:
            try:
                self.maintainer_id = int(configured_maintainer_id)
            except ValueError:
                logger.warning(
                    "[初始化] MAINTAINER_ID 不是有效的 Discord 使用者 ID，"
                    "將回退到 application owner"
                )
                self.maintainer_id = application.owner.id
        else:
            self.maintainer_id = application.owner.id

        if application.team is None:
            self.owner_id = application.owner.id
            self.owner_ids = set()
        else:
            self.owner_id = None
            self.owner_ids = {
                member.id
                for member in application.team.members
                if member.role
                in (discord.TeamMemberRole.admin, discord.TeamMemberRole.developer)
            }

        logger.info("[初始化] 載入核心管理模組")
        await self.load_extension(self.management_extension)

        for extension_name in self.discover_extension_names():
            full_path = self.extension_path(extension_name)
            if full_path is None or full_path == self.management_extension:
                continue

            try:
                logger.info(f"[初始化] 載入 Extension: {extension_name}")
                await self.load_extension(full_path)
            except Exception as error:
                logger.opt(exception=error).error(
                    f"[初始化] Extension 載入失敗: {extension_name}"
                )

        logger.info("[初始化] Extension 載入完畢")
        logger.info("[初始化] 同步斜線指令")
        slash_commands = await self.tree.sync()
        logger.info(f"[初始化] 已同步 {len(slash_commands)} 個斜線指令")

    async def on_ready(self) -> None:
        await self.change_presence(activity=discord.CustomActivity(name="無所事事中...."))
        logger.info(f"[初始化] {self.user} | Ready!")


bot = DiscordBot()


def _truncate(value: object, limit: int) -> str:
    text = str(value) if value is not None else "（無）"
    return text if len(text) <= limit else f"{text[: limit - 1]}…"


def _format_exception(error: BaseException) -> str:
    return "".join(
        traceback.format_exception(type(error), error, error.__traceback__)
    ).rstrip()


def _channel_description(guild: discord.Guild | None, channel: object) -> str:
    if guild is None:
        return "私人訊息"

    channel_name = getattr(channel, "name", None)
    if channel_name is None:
        channel_name = f"未知頻道 ({getattr(channel, 'id', '未知')})"
    return f"{guild.name}/{channel_name}"


async def _get_maintainer() -> discord.User | None:
    maintainer_id = bot.maintainer_id or bot.owner_id
    if maintainer_id is None:
        logger.error("[錯誤回報] 無法取得 maintainer ID")
        return None

    maintainer = bot.get_user(maintainer_id)
    if maintainer is not None:
        return maintainer

    try:
        return await bot.fetch_user(maintainer_id)
    except discord.HTTPException as error:
        logger.warning(f"[錯誤回報] 無法取得 maintainer: {error}")
        return None


async def _send_error_to_maintainer(embed: discord.Embed) -> None:
    maintainer = await _get_maintainer()
    if maintainer is None:
        return

    try:
        await maintainer.send(embed=embed)
    except discord.HTTPException as error:
        logger.warning(f"[錯誤回報] 無法私訊 maintainer: {error}")


@bot.event
async def on_command_error(
    ctx: commands.Context,
    error: commands.CommandError,
) -> None:
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, (commands.UserInputError, commands.CheckFailure)):
        logger.warning(f"[前綴指令] 使用者輸入或權限錯誤: {error}")
        return

    actual_error = error.original if isinstance(error, commands.CommandInvokeError) else error
    channel_description = _channel_description(ctx.guild, ctx.channel)
    logger.error(
        f"{channel_description}/{ctx.author.name}({ctx.author.id}):{actual_error}\n"
        f"{_format_exception(actual_error)}"
    )

    embed = discord.Embed(
        title="前綴指令錯誤",
        description=_truncate(actual_error, EMBED_DESCRIPTION_LIMIT),
        color=discord.Color.red(),
    )
    embed.set_author(
        name=_truncate(ctx.author.name, 256),
        icon_url=ctx.author.display_avatar.url,
    )
    embed.add_field(
        name="訊息內容",
        value=_truncate(getattr(ctx.message, "content", None), EMBED_FIELD_LIMIT),
        inline=False,
    )
    embed.add_field(
        name="頻道",
        value=_truncate(channel_description, EMBED_FIELD_LIMIT),
        inline=False,
    )
    await _send_error_to_maintainer(embed)


@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError,
) -> None:
    if isinstance(error, (app_commands.CheckFailure, app_commands.TransformerError)):
        logger.warning(f"[斜線指令] 使用者輸入或權限錯誤: {error}")
        if not interaction.response.is_done():
            await interaction.response.send_message(str(error), ephemeral=True)
        return

    actual_error = (
        error.original if isinstance(error, app_commands.CommandInvokeError) else error
    )
    channel_description = _channel_description(interaction.guild, interaction.channel)
    logger.error(
        f"{channel_description}/{interaction.user.name}({interaction.user.id}):"
        f"{actual_error}\n{_format_exception(actual_error)}"
    )

    if not interaction.response.is_done():
        try:
            await interaction.response.send_message(
                "執行指令時發生錯誤，已通知維護者。",
                ephemeral=True,
            )
        except discord.HTTPException as response_error:
            logger.warning(f"[錯誤回報] 無法回覆 interaction: {response_error}")

    embed = discord.Embed(
        title="斜線指令錯誤",
        description=_truncate(actual_error, EMBED_DESCRIPTION_LIMIT),
        color=discord.Color.red(),
    )
    embed.set_author(
        name=_truncate(f"{interaction.user.name} ({interaction.user.id})", 256),
        icon_url=interaction.user.display_avatar.url,
    )
    embed.add_field(
        name="指令資料",
        value=_truncate(interaction.data, EMBED_FIELD_LIMIT),
        inline=False,
    )
    embed.add_field(
        name="頻道",
        value=_truncate(channel_description, EMBED_FIELD_LIMIT),
        inline=False,
    )
    await _send_error_to_maintainer(embed)


def set_logger() -> None:
    logger.remove()
    debug_mode = os.getenv("DEBUG", "false").strip().lower() in ("true", "1", "yes")

    logger.add(sys.stdout, level="DEBUG" if debug_mode else "INFO", colorize=True)
    logger.add(
        BASE_DIR / "logs" / "system.log",
        rotation="7 days",
        retention="30 days",
        compression="zip",
        encoding="UTF-8",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )


def main() -> None:
    load_dotenv(BASE_DIR / ".env")
    set_logger()

    token = os.getenv("DISCORD_BOT_TOKEN", "").strip()
    if not token:
        logger.critical("DISCORD_BOT_TOKEN 尚未設定，請檢查 .env 或系統環境變數")
        raise SystemExit(1)

    try:
        bot.run(token)
    except Exception as error:
        logger.opt(exception=error).critical("無法啟動 Discord Bot")
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
