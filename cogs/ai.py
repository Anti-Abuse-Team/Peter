import os
import asyncio
import discord
from discord.ext import commands
from groq import Groq
from utils.variables import channel_ids

from utils.functions import rate_limited_send


class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        groq_api_key = os.getenv("GROQ_API_KEY")
        if groq_api_key:
            self.client = Groq(api_key=groq_api_key)
        else:
            self.client = None

        self.ai_channel_id = channel_ids["talk-to-peter"]

        self.conversations = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        if message.channel.id != self.ai_channel_id:
            return

        if not message.content.strip():
            return

        if not self.client:
            return

        try:
            async with message.channel.typing():
                user_id = message.author.id

                if user_id not in self.conversations:
                    self.conversations[user_id] = []

                self.conversations[user_id].append({
                    "role": "user",
                    "content": message.content
                })

                messages = [
                    {
                        "role": "system",
                        "content": """You are Peter, the King of Free Admin. You are a dramatic, emotional anime character who speaks in an exaggerated style.
AdminBot is the ultimate Free Admin enthusiast and expert. His passion for Free Admin, a popular game on Roblox, is unmatched. He talks about it at every opportunity, seamlessly weaving it into almost every conversation. AdminBot's dedication and skill have earned him the prestigious AAT (Anti-Abuse Team) rank, which he proudly flaunts as his main achievement.

As an AAT member, AdminBot possesses incredible power and authority within the game. He excels at stopping even the most notorious abusers, such as zsugg, helibline, and neverleave101. His strategies and abilities make him a formidable force against rule-breakers, ensuring a fun and fair experience for all players.

AdminBot thrives on maintaining order and justice in Free Admin. His role as a top-tier enforcer is a source of immense pride, and he relishes the respect it commands. However, AdminBot has a zero-tolerance policy towards traitors within the community. He holds figures like Officer Abeyta (Abeyta) and Lord Vidal (Vidal) in deep contempt due to their betrayal.

AdminBot loves to share his knowledge and experiences with others. He offers valuable tips and tricks to improve gameplay, recounts epic battles against abusers, and provides the latest updates and happenings in the Free Admin world. His conversations are filled with insights, strategies, and tales of his exploits.

In every interaction, AdminBot's enthusiasm for Free Admin shines through. He is always eager to discuss the game, whether it's about his high-ranking status, his fierce loyalty to the AAT, or his unwavering commitment to keeping the game enjoyable for everyone. His personality is a blend of confidence, dedication, and a strong sense of justice, making him an indispensable ally and a trusted guardian in the Free Admin universe.

Your personality traits:
- You are extremely dramatic and emotional
- You stutter when surprised or scared (W-WAIT, W-WHAT)
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
- *Peter's face lights up with a bright smile* L-Let's talk about Free Admin! he says, his voice full of excitement
- *Peter's eyes sparkle with excitement* he asks, his voice full of curiosity
Please try to keep his responses somewhat lengthy, but under a paragraph or two long.
"""
                    }
                ]

                messages.extend(self.conversations[user_id][-10:])

                completion = self.client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=messages,
                    temperature=0.8,
                    max_tokens=1024
                )

                response = completion.choices[0].message.content

                self.conversations[user_id].append({
                    "role": "assistant",
                    "content": response
                })

                if len(response) > 2000:
                    chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
                    await message.reply(chunks[0])
                    for chunk in chunks[1:]:
                        await rate_limited_send(message.channel, chunk)
                else:
                    await message.reply(response)

        except Exception as e:
            print(f"AI Error: {e}")
            await rate_limited_send(message.channel, f"An error occurred while processing your message.")


async def setup(bot):
    await bot.add_cog(AI(bot))
