from discord.ext import commands
from bot import NOMUtils
from .utils.context import Context
import discord
from random import randint, choice
from enum import Enum


# TODO: dissable buttons when the number cannot be that direction.


class Direction(Enum):
    HIGHER = 1
    LOWER = 0


class GameView(discord.ui.View):
    def __init__(self, *, timeout: float = 180):
        super().__init__(timeout=timeout)
        self.guess_range = [0, 10]  # The range of the game
        self.guess = randint(4, 6)  # The bot's inital guess
        self.possibilites = range(
            self.guess_range[0], self.guess_range[1] + 1
        )  # The possible numbers left to guess
        self.guesses: [int] = []
        self.colours = [
            discord.Color.green(),
            discord.Color.teal(),
            discord.Color.yellow(),
            discord.Color.orange(),
            discord.Color.red(),
        ]

        self.embed = discord.Embed(
            title=f"I guess **{self.guess}**", color=discord.Color.green()
        )

    def update_embed(self):
        self.embed.title = f"I guess **{self.guess}**"
        self.embed.color = self.colours[min(4, len(self.guesses))]

    async def handle_hint_response(
        self, interaction: discord.Interaction, hint: Direction
    ):
        self.guesses.append(self.guess)
        print("Poss before:", self.possibilites)
        if hint is Direction.HIGHER:
            self.possibilites = self.possibilites[
                self.possibilites.index(self.guess) + 1 :
            ]
        else:
            self.possibilites = self.possibilites[: self.possibilites.index(self.guess)]
        print("Poss after:", self.possibilites)
        print(self.possibilites, self.guesses)
        self.guess = choice(self.possibilites)

        self.update_embed()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label="lower", style=discord.ButtonStyle.primary)
    async def lower_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.guess == self.guess_range[0]:
            button.disabled = True
        await self.handle_hint_response(interaction, Direction.LOWER)

    @discord.ui.button(label="Got it!", style=discord.ButtonStyle.success)
    async def gotit_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.embed.title = "🥳"
        self.embed = self.embed.set_footer(text=f"Num was {self.guess}")

        await interaction.response.edit_message(embed=self.embed, view=None)
        self.stop()

    @discord.ui.button(label="higher", style=discord.ButtonStyle.blurple)
    async def higher_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.guess == self.guess_range[1]:
            button.disabled = True
        await self.handle_hint_response(interaction, Direction.HIGHER)


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot: NOMUtils = bot

    @commands.command()
    async def higher(self, ctx: Context, guess: int):
        num = randint(1, 10)
        if guess == num:
            await ctx.send("Congrats, that's the right number!")
        else:
            await ctx.send("higher" if guess < num else "lower")

    @commands.command()
    async def unhigher(self, ctx: Context):
        game_view = GameView()
        await ctx.send(embed=game_view.embed, view=game_view)
        await game_view.wait()
        # TODO: Handle timeout here


async def setup(bot):
    await bot.add_cog(Games(bot))
