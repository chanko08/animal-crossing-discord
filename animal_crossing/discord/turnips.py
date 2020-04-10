from discord.ext import commands
from animal_crossing.discord.argparse import DiscordArgumentParser, discord_argparse
import textwrap
import animal_crossing.turnips as turnips
import animal_crossing.turnips.price as price

def prediction_to_discord_message(pred):

    msg = "**Turnip Predictions**"
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
    @commands.command(name="turnips")
    async def list_turnip_price_predictions(self, ctx, *, arg_string):
        turnips_argp = DiscordArgumentParser()
        turnips_argp.add_argument("-buy-price", type=int, required=True, help="The price turnips was bought at on Sunday")
        turnips_argp.add_argument("-sell-prices", type=price.from_str, required=True, help="Comma-seperated list of the values observed in the week starting on Monday. Use zero to delimit unknown values between known values.")
        args = await discord_argparse(turnips_argp, ctx, arg_string)
        if args is None: return

        predictions = turnips.predict(args.buy_price, args.sell_prices)
        for p in predictions:
            await ctx.message.channel.send(prediction_to_discord_message(p))