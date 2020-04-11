from discord.ext import commands
import os
import dotenv
dotenv.load_dotenv()

from animal_crossing.discord.turnips import TurnipsCommand

bot = commands.Bot(command_prefix="!")
bot.add_cog(TurnipsCommand())


def main():
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__": main()
    