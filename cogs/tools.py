from discord.ext import tasks, commands
from random import randint
from asyncio import sleep

class Tools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_ctx = None
        self.current_vc_id = None
        self.inital_category = None

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)
    
    def cog_unload(self):
        self.vc_running.cancel()

    @tasks.loop(seconds=2.2)
    async def vc_evasion(self):
        ctx = self.current_ctx
        if ctx.author.voice and ctx.author.voice.channel.id == self.current_vc_id: #User is still in a vc
            category_count = len(ctx.guild.categories)
            if category_count > 1: #This only works if there is more than one category
                target_category = ctx.author.voice.channel.category
                while target_category == ctx.author.voice.channel.category: #If you get unlucky could cause a temporary ifinate loop
                    target_category = ctx.guild.categories[randint(0, category_count-1)]
                    # print(target_category.name, ctx.author.voice.channel.category.name)
                await ctx.author.voice.channel.move(end=True, category=target_category, sync_permissions=False)
        else: #The user has left the vc
            self.vc_evasion.cancel()
            await ctx.send(f'{ctx.author.mention} :x: You left the vc, so it has stoped running')

    @commands.command(hidden=True)
    async def vcrun(self, ctx):
        """Causes the vc to move around the server"""
        #Maybe add a thing where it returns it to og pos
        if ctx.author.voice:
            if self.vc_evasion.is_running():
                self.vc_evasion.stop()
                await ctx.author.voice.channel.move(end=True, category=self.inital_category, sync_permissions=False)
                self.current_ctx = None
                self.current_vc_id = None
                self.inital_category = None
                await ctx.send(':person_standing: Your vc is no longer on the run')
            else:
                self.current_ctx = ctx
                self.current_vc_id = ctx.author.voice.channel.id
                self.inital_category = ctx.author.voice.channel.category
                self.vc_evasion.start()
                await ctx.send(':person_running: Your vc is now on the run')
        else:
            await ctx.send('You are not in vc, so it cannot run')

    @commands.command(hidden=True, aliases=['vcint'])
    async def vcinterval(self, ctx, *, new_interval):
        # """Causes the vc to move around the server"""
        if self.vc_evasion.is_running(): #The interval is changable
            try:
                new_interval = float(new_interval)
            except:
                new_interval = False
                await ctx.send('`new_interval` was not an integer')
            if new_interval:
                new_interval = float(new_interval)
                self.vc_evasion.change_interval(seconds=new_interval)
                await ctx.send(f'Set interval to `{new_interval}`')
        else:
            await ctx.send('Your vc is not running')

    @commands.command(hidden=True)
    async def test(self, ctx):
        # webhook = await ctx.channel.create_webhook(name='DeletedUser')
        # webhooks = await ctx.channel.webhooks()
        # print(webhooks)
        # for webhook in webhooks:
        #     # print(webhook.user, ctx.me.name+ctx.me.name)
        #     # if webhook.user == ctx.me.name:
        #     #     print('Using a webhook')
        #     print(webhook.id) #853424812008931338
            # webhook_to_use = webhook
        for member in ctx.channel.members:
            webhook = await ctx.channel.create_webhook(name='DeletedUser')
            if member.nick:
                name_to_use = member.nick
            else:
                name_to_use = member.name
            await webhook.send(content='Testing :)', username=name_to_use, avatar_url=member.avatar_url)
            await webhook.delete()
            await sleep(0.5)

def setup(bot):
    bot.add_cog(Tools(bot))
