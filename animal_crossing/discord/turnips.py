import argparse
import textwrap
import pathlib
from datetime import date, timedelta

from discord.ext import commands

import animal_crossing.turnips as turnips
import animal_crossing.turnips.price as price
from animal_crossing.discord.argparse import DiscordArgumentParser, DiscordArgumentParserException

def positive_integer(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue

def turnip_sell_day(value):
    day_map = {
        "mon":0,
        "tue":1,
        "wed":2,
        "thu":3,
        "fri":4,
        "sat":5,
        "today":date.today().weekday()
    }

    if value == "today" and date.today().weekday() == 6:
        raise argparse.ArgumentTypeError(f"The choice 'today' is an invalid value on Sundays. Please use the 'buy' command to update Sunday prices")
    
    if value not in day_map:
        values = ", ".join(sorted([f"'{v}'" for v in day_map.keys()]))
        raise argparse.ArgumentTypeError(f"invalid choice: '{value}' (choose from {values}")
    
    return day_map[value]

def turnip_sell_time(value):
    time_map = {
        "am":0,
        "pm":1,
    }
    if value not in time_map:
        values = ", ".join(sorted([f"'{v}'" for v in time_map.keys()]))
        raise argparse.ArgumentTypeError(f"invalid choice: '{value}' (choose from {values}")
    
    return time_map[value]

def prediction_to_discord_message(preds):

    msg = "**Turnip Predictions**"
    for pred in preds:
        for i,prices in enumerate(pred.weeks):
            msg_part = f"""
            ```
            Pattern: {pred.pattern_name}
            Buy Price: {pred.base_price}
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
            msg_part = textwrap.dedent(msg_part)
            msg += msg_part
            msg += "\n"
    return msg








class TurnipsCommand(commands.Cog):
    def __init__(self, directory="/tmp/prices"):
        self.storage = pathlib.Path(directory)
        self.storage.mkdir(parents=True, exist_ok=True)

        argp = DiscordArgumentParser(prog="turnips")
        subp = argp.add_subparsers(required=True, dest="cmd")

        clip = subp.add_parser(
            "cli",
            help="Directly provide all known turnip values and recieve predictions."
        )
        clip.set_defaults(func=self.cli)
        clip.add_argument(
            "-buy-price",
            type=int,
            required=True,
            help="The price turnips was bought at on Sunday."
        )
        clip.add_argument(
            "-sell-prices",
            type=price.from_str,
            required=True,
            help="Comma-seperated list of the values observed in the week starting on Monday. Use zero to delimit unknown values between known values."
        )



        buyp = subp.add_parser(
            "buy",
            help="Update this week's Sunday buy price."
        )
        buyp.set_defaults(func=self.buy)
        buyp.add_argument(
            "price",
            type=positive_integer,
            help="Turnip price that was available on Sunday."
        )



        sellp = subp.add_parser(
            "sell",
            help="Update this week's sell prices and show a prediction."
        )
        sellp.set_defaults(func=self.sell)
        sellp.add_argument(
            "day",
            type=turnip_sell_day,
            help="Day of the week to update the sell price."
        )
        sellp.add_argument(
            "time",
            type=turnip_sell_time,
            help="Time of day the sell price was observed."
        )
        sellp.add_argument(
            "price",
            type=positive_integer,
            help="Price of turnips in bells."
        )



        resetp = subp.add_parser(
            "reset",
            help="Reset/clear values for this week"
        )
        resetp.set_defaults(func=self.reset)



        showp = subp.add_parser(
            "show",
            help="Show predicted turnip prices for this week"
        )
        showp.set_defaults(func=self.show)

        self.argp = argp

    @commands.command(rest_is_raw=True)
    async def turnips(self, ctx, *, args):
        try:
            args = self.argp.parse_args([a.strip() for a in args.split()])
        except DiscordArgumentParserException as e:
            return await e.send_message(ctx)
        
        await args.func(ctx, args)

    async def cli(self, ctx, args):
        predictions = turnips.predict(args.buy_price, args.sell_prices)
        await ctx.message.channel.send(prediction_to_discord_message(predictions))
    
    async def reset(self, ctx, args):
        user = ctx.author.name
        user_id = ctx.author.id
        user_dir = self.storage / f"{user}--{user_id}"
        user_dir.mkdir(parents=True, exist_ok=True)

        sunday = date.today() - timedelta(days=date.today().weekday() + 1)
        if date.today().weekday() == 6:
            sunday = date.today()
        
        prices_file = user_dir / sunday.strftime("%Y-%m-%d")
        prices_file.unlink()
        await ctx.message.channel.send("```\nCleared values out for this week\n```")
    

    async def show(self, ctx, args):
        buy_price, sell_prices = self._read_user_file(ctx.author.name, ctx.author.id)
        if buy_price < 1:
            await ctx.message.channel.send("```\nBuy price is required to show turnip price predictions\n```")
            return
        predictions = turnips.predict(buy_price, sell_prices)
        await ctx.message.channel.send(prediction_to_discord_message(predictions))
    
    async def sell(self, ctx, args):
        buy_price, sell_prices = self._read_user_file(ctx.author.name, ctx.author.id)

        sell_price_index = args.day * 2 + args.time
        sell_prices[sell_price_index] = args.price

        self._write_user_file(ctx.author.name, ctx.author.id, buy_price, sell_prices)
        await self.show(ctx, None)
    
    async def buy(self, ctx, args):
        buy_price, sell_prices = self._read_user_file(ctx.author.name, ctx.author.id)
        self._write_user_file(ctx.author.name, ctx.author.id, args.price, sell_prices)
        await self.show(ctx, None)

    def _get_user_file(self, user, user_id):
        user_dir = self.storage / f"{user}--{user_id}"
        user_dir.mkdir(parents=True, exist_ok=True)

        sunday = date.today() - timedelta(days=date.today().weekday() + 1)
        if date.today().weekday() == 6:
            sunday = date.today()
        
        prices_file = user_dir / sunday.strftime("%Y-%m-%d")
        return prices_file

    def _read_user_file(self, user, user_id):
        prices_file = self._get_user_file(user, user_id)

        buy_price = 0
        sell_prices = {}
        if prices_file.exists():
            with open(prices_file, "r") as f:
                values = [int(x.strip()) for x in f.readline().split(",")]
                buy_price = values.pop(0)
                sell_prices = {i:v for i,v in enumerate(values) if v > 0}
                
        return (buy_price, sell_prices)
        
    def _write_user_file(self, user, user_id, buy_price, sell_prices):
        prices_file = self._get_user_file(user, user_id)


        output = ",".join([str(buy_price)] + [str(sell_prices.get(i, 0)) for i in range(12)])
        with open(prices_file, "w") as f:
            f.write(output)
        