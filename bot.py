import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import json
import os

with open('data.json') as e:
    configs = json.load(e)
    token = configs['token']
    prefix = configs['prefix']

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True
ADV_DURATION = 60 * 1

bot = commands.Bot(command_prefix=prefix, intents=intents)



if os.path.exists('advs.json'):
    with open('advs.json', 'r') as f:
        advs = json.load(f)
else:
    advs = {}




def save_advs():
    with open('advs.json', 'w') as f:
        json.dump(advs, f)




@tasks.loop(seconds=60)
async def checkadvs():
    to_remove = []
    now = datetime.utcnow()
    for user_id, adv_info in advs.items():
        expiry_time = datetime.fromisoformat(adv_info['expiry'])
        if now >= expiry_time:
            to_remove.append(user_id)
    for user_id in to_remove:
        del advs[user_id]
    if to_remove:
        save_advs()



@bot.event
async def on_ready():
    checkadvs.start()
    print(f'Bot {bot.user.name} está pronto!')




def has_role(roleid):
    async def pred(ctx):
         role = discord.utils.get(ctx.author.roles, id=roleid)
         return role is not None
    return commands.check(pred)




@bot.command(name='adv')
@commands.has_permissions(administrator=True)
@has_role(1249840183839559763)
async def adv(ctx, member: discord.Member, duration: int, roleid: int):
    role = ctx.guild.get_role(roleid)
    expiry_time = datetime.utcnow() + timedelta(seconds=int(duration))
    advs[str(member.id)] = {
        'expiry': expiry_time.isoformat()
    }
    save_advs()
    await member.add_roles(role)
    channel = bot.get_channel(1249774077258764411)
    await channel.send(f'<@{member.id}> foi advertido por <@{ctx.author.id}>')
    try:
        await member.send(f'Você recebeu uma advertência que expirará em {(duration / 60):.2f} minutos.')
    except discord.Forbidden:
        await ctx.send(f'Não consegui enviar uma DM para {member.mention}.')
    await ctx.send(f'{member.mention} recebeu uma advertência.')




@bot.command(name='remove_adv')
@has_role(1249840183839559763)
@commands.has_permissions(administrator=True)
async def remove_adv(ctx, member: discord.Member):
    if str(member.id) in advs:
        del advs[str(member.id)]
        save_advs()
        await ctx.send(f'A advertência de {member.mention} foi removida.')
    else:
        await ctx.send(f'{member.mention} não tem advertências.')




@bot.command(name='check_adv')
async def checkadv(ctx, member: discord.Member):
    if str(member.id) in advs:
        expiry_time = datetime.fromisoformat(advs[str(member.id)]['expiry'])
        remaining_time = expiry_time - datetime.utcnow()
        minutes, seconds = divmod(remaining_time.total_seconds(), 60)
        await ctx.send(f'{member.mention} tem uma advertência que expirará em {int(minutes)} minutos e {int(seconds)} segundos.')
    else:
        await ctx.send(f'{member.mention} não tem advertências.')



bot.run(token)
