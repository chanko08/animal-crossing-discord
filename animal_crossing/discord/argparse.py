import argparse
from contextlib import redirect_stdout, redirect_stderr
import io
import sys

class DiscordArgumentParserException(Exception):
    def __init__(self, status, messages):
        self.status = status
        self.messages = messages
    
    async def send_message(self, ctx):
        message = "\n".join(self.messages)
        await ctx.message.channel.send(f"```\n{message}\n```")
        

class DiscordArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.messages = []

    def _print_message(self, message, file=None):
        self.messages.append(message)

    def exit(self, status=0, message=None):
        if message:
            self._print_message(message)

        raise DiscordArgumentParserException(status, self.messages)