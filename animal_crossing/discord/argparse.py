import argparse

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