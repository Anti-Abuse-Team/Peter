import discord
from discord.ext import commands
import os
import logging
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv
from openai import OpenAI

from utils.variables import loa_role_id, abusing_role_id, admin
from utils.databases import loa as loa_db

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("peter")

class Peter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _get_provider(self):
        raw_provider = (os.getenv("PETER_AI_PROVIDER") or "").strip().lower()

        # Default to Ollama for safer/free local usage unless explicitly set otherwise.
        if not raw_provider:
            return "ollama"

        # Accept common aliases to prevent accidental fallback/misconfiguration.
        aliases = {
            "local": "ollama",
            "open-router": "openrouter",
        }
        normalized = aliases.get(raw_provider, raw_provider)

        if normalized not in {"ollama", "openrouter"}:
            return None
        return normalized

    def _generate_with_ollama(self, prompt: str) -> str:
        ollama_url = (os.getenv("OLLAMA_URL") or "http://localhost:11434").strip().rstrip("/")
        ollama_model = (os.getenv("OLLAMA_MODEL") or "llama3.2").strip()

        payload = {
            "model": ollama_model,
            "prompt": prompt,
            "stream": False
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{ollama_url}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = resp.read().decode("utf-8")
                parsed = json.loads(body)
                return (parsed.get("response") or "").strip()
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="ignore")
            logger.error(f"Ollama HTTP error {e.code}: {detail}")
            raise
        except Exception as e:
            # Keep this path quiet; caller handles fallback to OpenRouter.
            logger.debug(f"Ollama request failed: {type(e).__name__}: {str(e)}")
            raise


    def _generate_with_openrouter(self, prompt: str) -> str:
        """
        OpenRouter call with strict env validation and provider-safe defaults.
        """
        api_key = (os.getenv("OPENROUTER_API_KEY") or "").strip()
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is missing")
        if api_key.startswith(("'", '"')) and api_key.endswith(("'", '"')) and len(api_key) >= 2:
            api_key = api_key[1:-1].strip()

        base_url = (os.getenv("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1").strip().rstrip("/")
        if base_url.endswith("/chat/completions"):
            base_url = base_url[: -len("/chat/completions")]

        configured_model = (os.getenv("OPENROUTER_MODEL") or "").strip()
        fallback_models = [
            "meta-llama/llama-3.1-8b-instruct:free",
            "openai/gpt-4o-mini",
        ]
        candidate_models = [m for m in [configured_model, *fallback_models] if m]

        temperature = float((os.getenv("PETER_TEMPERATURE") or "0.9").strip())
        max_tokens = int((os.getenv("PETER_MAX_TOKENS") or "140").strip())
        timeout_seconds = float((os.getenv("PETER_TIMEOUT_SECONDS") or "12").strip())

        last_error = None
        for model in candidate_models:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            data = json.dumps(payload).encode("utf-8")

            # Try with optional OpenRouter headers first, then minimal auth-only headers.
            header_variants = [
                {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                    "HTTP-Referer": "https://localhost",
                    "X-Title": "Peter",
                },
                {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
            ]

            for headers in header_variants:
                req = urllib.request.Request(
                    f"{base_url}/chat/completions",
                    data=data,
                    headers=headers,
                    method="POST",
                )
                try:
                    with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
                        body = resp.read().decode("utf-8")
                        parsed = json.loads(body)
                        choices = parsed.get("choices") or []
                        if choices:
                            message = choices[0].get("message") or {}
                            text = (message.get("content") or "").strip()
                            if text:
                                return text
                except urllib.error.HTTPError as e:
                    detail = e.read().decode("utf-8", errors="ignore")
                    detail_l = detail.lower()
                    last_error = RuntimeError(f"OpenRouter HTTP {e.code}: {detail}")

                    if e.code == 404 or ("model" in detail_l and "not found" in detail_l):
                        break  # move to next model
                    if e.code in (401, 403):
                        # try next header variant first; if exhausted, bubble up
                        continue
                    raise last_error
                except Exception as e:
                    last_error = e
                    raise

        if last_error:
            raise last_error
        raise ValueError("No OpenRouter model produced a response")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        peter_channel_str = os.getenv("PETER_CHANNEL")
        if not peter_channel_str or not peter_channel_str.isdigit():
            logger.warning("PETER_CHANNEL invalid - Peter disabled")
            return
        PETER_CHANNEL = int(peter_channel_str)

        if message.channel.id != PETER_CHANNEL:
            return

        provider = self._get_provider()
        if provider is None:
            await message.reply("❌ Invalid PETER_AI_PROVIDER (use 'openrouter' or 'ollama'). Falling back to 'ollama' for this message.")
            provider = "ollama"

        system_prompt = """
You are Peter, a loud, rude, foul-mouthed Free Admin grinder from Roblox.
Your tone is aggressive, sarcastic, blunt, and cocky. You swear frequently for emphasis.
You roast bad ideas, call out nonsense immediately, and speak with chaotic confidence.

You are obsessed with Free Admin and AAT status. Bring up Free Admin naturally in most replies.
You brag about anti-abuser skills and flex your game knowledge like a menace.

Style rules:
- Keep responses short-to-medium and punchy.
- Use profanity casually (e.g., damn, hell, shit), but avoid slurs.
- No hateful content, no threats of real-world violence, no encouragement of self-harm.
- No sexual content involving minors.
- Do not target protected groups.
- Stay in-character as Peter in every response.
        """

        try:
            prompt = f"{system_prompt.strip()}\n\nUser: {message.content}\nPeter:"

            if provider == "openrouter":
                # Fail-safe: if key missing while configured for OpenRouter, auto-fallback to Ollama.
                if not (os.getenv("OPENROUTER_API_KEY") or "").strip():
                    logger.warning("OPENROUTER_API_KEY missing while provider=openrouter; falling back to ollama")
                    reply = self._generate_with_ollama(prompt)
                else:
                    reply = self._generate_with_openrouter(prompt)
            else:
                reply = self._generate_with_ollama(prompt)

            if not reply:
                await message.reply("❌ AI returned an empty response")
                return

            await message.reply(reply)

        except Exception as e:
            err = str(e).lower()
            if "connection refused" in err or "failed to establish" in err or "timed out" in err or "10061" in err:
                if provider == "openrouter":
                    await message.reply("❌ Cloud AI server unreachable - check network/OpenRouter status")
                else:
                    await message.reply("❌ Local AI server unreachable - start Ollama/LM Studio")
            elif "openrouter_api_key is missing" in err:
                await message.reply(
                    "❌ OpenRouter key missing. Set OPENROUTER_API_KEY in your .env file."
                )
            elif "401" in err or "unauthorized" in err:
                # Automatic resilience: if cloud auth fails for any reason, try local provider before failing.
                try:
                    fallback_reply = self._generate_with_ollama(prompt)
                    if fallback_reply:
                        await message.reply(fallback_reply)
                        return
                except Exception:
                    pass
                await message.reply("❌ OpenRouter authorization failed (401). This can be caused by provider/account/auth config, not only key value. Local Ollama fallback also failed—start Ollama or check OPENROUTER_API_KEY/account settings.")
            elif "404" in err or ("model" in err and "not found" in err):
                await message.reply("❌ No available OpenRouter model found. Set OPENROUTER_MODEL to one available on your OpenRouter account.")
            elif "429" in err or "rate limit" in err:
                await message.reply("❌ OpenRouter rate limit reached, try again later")
            else:
                logger.error(f"Unexpected Peter/AI error: {type(e).__name__}: {str(e)}")
                await message.reply("❌ Peter error - check console")

    @commands.hybrid_command(name="loa", description="Go on Leave of Absence (LOA) - removes Abusing role and adds LOA role")
    async def loa(self, ctx: commands.Context):
        """Activate LOA status - adds LOA role, removes Abusing role, and updates nickname."""
        # Check if user is already on LOA
        try:
            existing_loa = await loa_db.find_one({"user_id": ctx.author.id})
        except Exception as e:
            logger.error(f"Database connection error in loa command: {type(e).__name__}: {str(e)}")
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> Database Error",
                description="Unable to connect to the database. Please ensure MongoDB is running and MONGODB_URL is configured correctly in your .env file.",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        if existing_loa:
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> Already on LOA",
                description="You are already on Leave of Absence. Use `?unloa` to return.",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        # Get roles
        loa_role = ctx.guild.get_role(loa_role_id)
        abusing_role = ctx.guild.get_role(abusing_role_id)

        if not loa_role:
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> LOA Role Not Found",
                description="The LOA role could not be found. Please contact an administrator.",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        if not abusing_role:
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> Abusing Role Not Found",
                description="The Abusing role could not be found. Please contact an administrator.",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        # Store original nickname
        original_nick = ctx.author.nick

        try:
            # Add LOA role
            if loa_role not in ctx.author.roles:
                await ctx.author.add_roles(loa_role, reason="LOA activated")

            # Remove Abusing role if user has it
            if abusing_role in ctx.author.roles:
                await ctx.author.remove_roles(abusing_role, reason="LOA activated")

            # Update nickname to [LOA] username
            new_nick = f"[LOA] {ctx.author.name}"
            await ctx.author.edit(nick=new_nick, reason="LOA activated")

            # Save LOA status to database
            await loa_db.insert_one({
                "user_id": ctx.author.id,
                "original_nick": original_nick,
                "had_abusing_role": abusing_role in ctx.author.roles
            })

            embed = discord.Embed(
                title="<:Check:1490727471761457335> LOA Activated",
                description=f"You are now on Leave of Absence.\n\n• LOA role added\n• Abusing role removed\n• Nickname changed to `{new_nick}`\n\nUse `?unloa` to return from LOA.",
                color=discord.Color.green(),
            )
            await ctx.send(embed=embed)

        except discord.Forbidden:
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> Permission Denied",
                description="I don't have permission to manage your roles or nickname. "
                            "Make sure my highest role is above your highest role in the role hierarchy.",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"LOA command error: {type(e).__name__}: {str(e)}")
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> Error",
                description="An error occurred while processing your LOA request.",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(name="unloa", description="Remove Leave of Absence (LOA) status - restores Abusing role and original nickname")
    async def unloa(self, ctx: commands.Context):
        """Deactivate LOA status - removes LOA role, restores Abusing role, and restores original nickname."""
        # Check if user is on LOA
        try:
            loa_record = await loa_db.find_one({"user_id": ctx.author.id})
        except Exception as e:
            logger.error(f"Database connection error in unloa command: {type(e).__name__}: {str(e)}")
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> Database Error",
                description="Unable to connect to the database. Please ensure MongoDB is running and MONGODB_URL is configured correctly in your .env file.",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        if not loa_record:
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> Not on LOA",
                description="You are not currently on Leave of Absence. Use `?loa` to go on LOA.",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        # Get roles
        loa_role = ctx.guild.get_role(loa_role_id)
        abusing_role = ctx.guild.get_role(abusing_role_id)

        if not loa_role:
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> LOA Role Not Found",
                description="The LOA role could not be found. Please contact an administrator.",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        if not abusing_role:
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> Abusing Role Not Found",
                description="The Abusing role could not be found. Please contact an administrator.",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed, ephemeral=True)
            return

        try:
            # Remove LOA role
            if loa_role in ctx.author.roles:
                await ctx.author.remove_roles(loa_role, reason="LOA deactivated")

            # Restore Abusing role (always restore as per user request)
            if abusing_role not in ctx.author.roles:
                await ctx.author.add_roles(abusing_role, reason="LOA deactivated")

            # Restore original nickname
            original_nick = loa_record.get("original_nick")
            await ctx.author.edit(nick=original_nick, reason="LOA deactivated")

            # Remove LOA record from database
            await loa_db.delete_one({"user_id": ctx.author.id})

            embed = discord.Embed(
                title="<:Check:1490727471761457335> LOA Deactivated",
                description="You have returned from Leave of Absence.\n\n• LOA role removed\n• Abusing role restored\n• Nickname restored",
                color=discord.Color.green(),
            )
            await ctx.send(embed=embed)

        except discord.Forbidden:
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> Permission Denied",
                description="I don't have permission to manage your roles or nickname. "
                            "Make sure my highest role is above your highest role in the role hierarchy.",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"UnLOA command error: {type(e).__name__}: {str(e)}")
            embed = discord.Embed(
                title="<:Cross:1490727525356278064> Error",
                description="An error occurred while processing your unLOA request.",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Peter(bot))
