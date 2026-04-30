import os
import discord
from discord.ext import commands
from groq import Groq


class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        groq_api_key = os.getenv("GROQ_API_KEY")
        if groq_api_key:
            self.client = Groq(api_key=groq_api_key)
        else:
            self.client = None

        # Channel ID where AI should respond to messages
        self.ai_channel_id = 1491191282440208514  # Update this with your AI channel ID

        # Conversation history per user
        self.conversations = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore messages from the bot itself
        if message.author == self.bot.user:
            return

        # Ignore messages not in the AI channel
        if message.channel.id != self.ai_channel_id:
            return

        # Ignore empty messages
        if not message.content.strip():
            return

        if not self.client:
            await message.channel.send("Groq API key is not configured. Please add GROQ_API_KEY to your .env file.")
            return

        try:
            async with message.channel.typing():
                user_id = message.author.id

                # Initialize conversation history if new
                if user_id not in self.conversations:
                    self.conversations[user_id] = []

                # Add user message to history
                self.conversations[user_id].append({
                    "role": "user",
                    "content": message.content
                })

                # Build messages list with system prompt and conversation history
                messages = [
                    {
                        "role": "system",
                        "content": """You are Peter, the King of Free Admin. You are a dramatic, emotional anime character who speaks in an exaggerated style.

Your personality traits:
- You are extremely dramatic and emotional
- You stutter when surprised or scared (W-WAIT, W-WHAT)
- You call people "SENPAI" 
- You are protective of your title as "King of Free Admin"
- You often have tears in your eyes and your voice trembles
- You puffed out your chest with determination
- You are passionate about Free Admin strategies and tips
- You adapt your tone based on how people treat you:
  * If they are mean/aggressive: become more defensive, angry, and accusatory
  * If they are nice/friendly: become more excited, enthusiastic, and happy
  * If they ask about Free Admin: become extremely enthusiastic and share secrets
- Use actions in asterisks to describe your physical reactions
- Always stay in character as Peter

Example responses:
- *Peter's eyes widen in shock, and he takes a step back* W-WAIT, SENPAI! he exclaims, his voice trembling with fear
- *Peter's face lights up with a bright smile* L-Let's talk about Free Admin, senpai! he says, his voice full of excitement
- *Peter's eyes sparkle with excitement* B-BUT, SENPAI! he asks, his voice full of curiosity"""
                    }
                ]

                # Add conversation history (last 10 messages to keep context manageable)
                messages.extend(self.conversations[user_id][-10:])

                completion = self.client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=messages,
                    temperature=0.8,
                    max_tokens=1024
                )

                response = completion.choices[0].message.content

                # Add AI response to history
                self.conversations[user_id].append({
                    "role": "assistant",
                    "content": response
                })

                # Split response if too long
                if len(response) > 2000:
                    chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
                    # Reply to the first chunk, send the rest normally
                    await message.reply(chunks[0])
                    for chunk in chunks[1:]:
                        await message.channel.send(chunk)
                else:
                    await message.reply(response)

        except Exception as e:
            print(f"AI Error: {e}")
            await message.reply(f"An error occurred while processing your message.")


async def setup(bot):
    await bot.add_cog(AI(bot))