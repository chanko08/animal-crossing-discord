import argparse
import textwrap
import pathlib
from datetime import date, timedelta

from discord.ext import commands

import animal_crossing.turnips as turnips
import animal_crossing.turnips.price as price


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


DAYS = {"mon":0, "tue":1, "wed":2, "thu":3, "fri":4, "sat":5} #sunday purposefully omitted
def turnip_day(value : str):
    
    if value[:3].lower() not in DAYS.keys():
        raise BadArgument(f"Day '{value}' passed is not a valid day. Choices are {tuple(sorted(DAYS.keys()))}.")
    
    return value.lower()



TIMES = {"am":0, "pm":1}
def turnip_time(value : str):
    
    if value.lower() not in TIMES.keys():
        raise BadArgument(f"Time '{value}' passed is not a valid day. Choices are {tuple(sorted(TIMES.keys()))}.")
    
    return value.lower()



def turnip_price(value : str):
    try:
        value = int(value)
    except ValueError as e:
        raise BadArgument("Price value passed is not a valid integer")
    
    if value < 1: raise BadArgument(f"Price '{value}' is not a valid price. Price must be greater than zero.")
    return value

    


class TurnipsCommand(commands.Cog):
    def __init__(self, directory="/tmp/prices"):
        self.storage = pathlib.Path(directory)
        self.storage.mkdir(parents=True, exist_ok=True)

    @commands.command()
    async def show(self, ctx):
        buy_price, sell_prices = self._read_user_file(ctx.author.name, ctx.author.id)
        if buy_price < 1:
            await ctx.message.channel.send("```\nBuy price is required to show turnip price predictions\n```")
            return
        predictions = turnips.predict(buy_price, sell_prices)
        await ctx.message.channel.send(prediction_to_discord_message(predictions))



    @commands.command()
    async def sell(self, ctx, day:turnip_day, time:turnip_time, price:turnip_price):
        buy_price, sell_prices = self._read_user_file(ctx.author.name, ctx.author.id)

        sell_price_index = DAYS[day] * 2 + TIMES[time]
        sell_prices[sell_price_index] = price

        self._write_user_file(ctx.author.name, ctx.author.id, buy_price, sell_prices)
        await self.show(ctx)
    
    @sell.error
    async def sell_args_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(str(error))



    @commands.command()
    async def buy(self, ctx, price:turnip_price):
        buy_price, sell_prices = self._read_user_file(ctx.author.name, ctx.author.id)
        self._write_user_file(ctx.author.name, ctx.author.id, price, sell_prices)
        await self.show(ctx)
    
    @buy.error
    async def buy_args_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(str(error))


    
    @commands.command()
    async def reset(self, ctx):
        self._get_user_file(ctx.author.name, ctx.author.id).unlink()
        await ctx.message.channel.send("```\nCleared values out for this week\n```")






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