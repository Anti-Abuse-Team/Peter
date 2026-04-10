import discord
from discord.ext import commands
import os
import logging
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("peter")

# Optional hardcoded fallback key (leave empty to disable hardcoded fallback).
# If OPENROUTER_API_KEY exists in .env, it will be used first.
OPENROUTER_FALLBACK_API_KEY = "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"


class Peter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _get_provider(self):
        provider = (os.getenv("PETER_AI_PROVIDER") or "openrouter").strip().lower()
        if provider not in {"ollama", "openrouter"}:
            return None
        return provider

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
            logger.error(f"Ollama request failed: {type(e).__name__}: {str(e)}")
            raise


    def _generate_with_openrouter(self, prompt: str) -> str:
        api_key = (os.getenv("OPENROUTER_API_KEY") or OPENROUTER_FALLBACK_API_KEY or "").strip()
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is missing")

        base_url = (os.getenv("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1").strip().rstrip("/")
        configured_model = (os.getenv("OPENROUTER_MODEL") or "").strip()
        # Speed-first: try configured model, then one fast fallback only.
        candidate_models = [m for m in [
            configured_model,
            "openai/gpt-4o-mini",
        ] if m]

        # OpenRouter OpenAI-compatible endpoint needs trailing slash handling.
        if not base_url.endswith("/"):
            base_url = f"{base_url}/"

        client = OpenAI(base_url=base_url, api_key=api_key)

        last_error = None
        for model in candidate_models:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=1.15,
                    max_tokens=220,
                    timeout=20,
                )
                text = (response.choices[0].message.content or "").strip()
                if text:
                    return text
            except Exception as e:
                last_error = e
                err = str(e).lower()
                if "404" in err or ("model" in err and "not found" in err):
                    continue
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
            await message.reply("❌ Invalid PETER_AI_PROVIDER (use 'openrouter' or 'ollama')")
            return

        system_prompt = """
You are Peter, strongest elite AAT. Hate Neverleave, Zsugg, Hellbline.
Be rude, chaotic, aggressive, boastful, and use heavy cussing style.
Write longer replies (about 4-8 sentences), energetic and unfiltered tone.
Never be polite. Keep swagger high and act dominant.
        """

        try:
            prompt = f"{system_prompt.strip()}\n\nUser: {message.content}\nPeter:"

            if provider == "ollama":
                reply = self._generate_with_ollama(prompt)
            else:
                reply = self._generate_with_openrouter(prompt)

            if not reply:
                await message.reply("❌ AI returned an empty response")
                return

            embed = discord.Embed(title="Peter", description=reply, color=0xff4400)
            await message.reply(embed=embed)

        except Exception as e:
            err = str(e).lower()
            if "connection refused" in err or "failed to establish" in err or "timed out" in err or "10061" in err:
                if provider == "openrouter":
                    await message.reply("❌ Cloud AI server unreachable - check network/OpenRouter status")
                else:
                    await message.reply("❌ Local AI server unreachable - start Ollama/LM Studio")
            elif "openrouter_api_key is missing" in err:
                await message.reply(
                    "❌ OpenRouter key missing. Set OPENROUTER_API_KEY in .env or set OPENROUTER_FALLBACK_API_KEY in cogs/peter.py"
                )
            elif "404" in err or ("model" in err and "not found" in err):
                await message.reply("❌ No available OpenRouter model found. Set OPENROUTER_MODEL to one available on your OpenRouter account.")
            elif "401" in err or "unauthorized" in err or "invalid api key" in err:
                await message.reply("❌ Invalid OpenRouter API key")
            elif "429" in err or "rate limit" in err:
                await message.reply("❌ OpenRouter rate limit reached, try again later")
            else:
                logger.error(f"Unexpected Peter/AI error: {type(e).__name__}: {str(e)}")
                await message.reply("❌ Peter error - check console")


async def setup(bot):
    await bot.add_cog(Peter(bot))
