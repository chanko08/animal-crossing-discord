import os
import argparse
import functools
import textwrap
import discord
from discord.ext import commands
import dotenv

import turnips
dotenv.load_dotenv()



class DiscordArgumentParserException(Exception):
    def __init__(self, argp, message):
        self.argp = argp
        self.message = message

class DiscordArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise DiscordArgumentParserException(self, message)

async def discord_argparse(argp, ctx, arg_string):
    try:
        args = argp.parse_args([x.strip() for x in arg_string.split()])

    except DiscordArgumentParserException as e:
        msg = "```\n"
        msg += e.argp.format_usage()
        msg += e.message
        msg += "```"

        await ctx.message.channel.send(msg)
        return None
    return args


def pattern_to_message(buy_price, pattern, prices):
    msg = f"""
    **Turnip Predictions**
    ```
    Pattern: {pattern}
    Buy Price: {buy_price}
    Mon AM: {prices[0]}
        PM: {prices[1]}
    Tue AM: {prices[2]}
        PM: {prices[3]}
    Wed AM: {prices[4]}
        PM: {prices[5]}
    Thu AM: {prices[6]}
        PM: {prices[7]}
    Fri AM: {prices[8]}
        PM: {prices[9]}
    Sat AM: {prices[10]}
        PM: {prices[11]}    
    ```
    """
    msg = textwrap.dedent(msg)
    return msg


def prices(s):
    values = [int(v.strip()) for v in s.split(",")]
    week = {i:v for i,v in enumerate(values) if v > 0}
    return week


bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")


@bot.command(name="turnips")
async def command_turnips(ctx, *, arg_string):
    turnips_argp = DiscordArgumentParser()
    turnips_argp.add_argument("-buy-price", type=int, required=True, help="The price turnips was bought at on Sunday")
    turnips_argp.add_argument("-sell-prices", type=prices, required=True, help="Comma-seperated list of the values observed in the week starting on Monday. Use zero to delimit unknown values between known values.")
    args = await discord_argparse(turnips_argp, ctx, arg_string)
    if args is None: return

    matches = turnips.find_pattern_matches(args.sell_prices, args.buy_price)
    if not any([len(ps) for pattern, ps in matches.items()]):
        print("No matches found for provided parameters")
        return

    

    for pattern, predictions in matches.items():
        if len(predictions) == 0: continue
        summary_prediction = turnips.patterns.consolidate_predictions(predictions)
        summary_prediction = turnips.patterns.replace_predictions_with_data(args.sell_prices, summary_prediction)
        summary_prediction = turnips.patterns.prediction_rates_to_str(summary_prediction)

        msg = pattern_to_message(args.buy_price, pattern, summary_prediction)
        await ctx.message.channel.send(msg)


def main():
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__": main()
    
    
