import discord
import emojis
import random
import openai
import pickle
import requests
import json
import asyncio
loaded_trusted_roles = {}
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = discord.Bot(intents=intents)
openai.api_key = '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'

async def trusted_role_check(guild, guild_member):
    try:
        global loaded_trusted_roles
        with open('trusted_roles', 'rb') as trusted_roles:
            global loaded_trusted_roles
            loaded_trusted_roles = pickle.load(trusted_roles)
    except EOFError:
        loaded_trusted_roles = {}
    try:
        has_trusted_role = guild_member.get_role(loaded_trusted_roles[str(guild.id)])
        return bool(has_trusted_role)
    except KeyError:
        print("no trusted role found")
        return False

def trusted_role_command(func):
    async def wrapper(*args, **kwargs):
        if await trusted_role_check(args[0].guild, args[0].author) or args[0].author.id == 753541396006436906:
            await func(*args, **kwargs)
        else:
            await args[0].channel.send("No permissions")
    return wrapper

async def amogus(message, args):
    await message.channel.send("amogus")

async def hardcore_says(message, args):
    args_with_spaces = args
    for arg_num, arg in enumerate(args):
        args_with_spaces[arg_num] = arg + ' '

    await message.channel.send(''.join(args_with_spaces))
    await message.delete()

async def clone_channel(message, args):
    for x in range(int(args[1])):
        await message.channel_mentions[0].clone()

async def hardcore_helps(message, args):
    help_message = '''*Commands avaiable for everyone:*
`help` - shows this message
`amogus` - amogus
`say <text>` - make this client say whatever you want
`random_reaction <message link>` - reacts with random emoji to any message
`random_mention <how many times>` - mentions random member
`roll_dice <how many dices> <how many sides>` - simulates rolling dice
`flip_coin <how many times>` - simulates flipping coin
`hardcoregpt <prompt>` - ask HardcoreGPT anything
`say_in_channel <text> <channel>` - make this client say whatever you want, in any channel
`confuse` - reply with a random, nonsensical message
`random_emoji` - make client say random emoji
*Commands avaiable only for members with trusted role:*
`delete_channel <channel>` - delete channel
`delete_all <channel name>` - delete all channels with given name
`create_channel <channel name> <category name>` - create channel
`ban <member>` - ban member
`kick <member>` - kick member
`remove_roles <member> <roles>` - remove roles from member
`give_roles <member> <roles>` - gives roles to member
*Commands avaiable only for the owner:*
`set_trusted_role <role>` - sets the trusted role
**How to use client commands:**
Hardcore <command name> <command argument 1> <command argument 2>'''
    help_embed = discord.Embed(color=discord.Colour(0x00ff00), title='List of commands for Hardcore client', description=help_message)
    await message.reply(embed=help_embed)

async def random_reaction(message, args):
    list_of_emojis = emojis.db.get_emoji_aliases().values()
    list_of_emojis = list(list_of_emojis)
    message_to_react = args[0]
    message_to_react = message_to_react.split('/')
    message_to_react = int(message_to_react[len(message_to_react)-1])
    message_to_react = message.channel.get_partial_message(message_to_react)
    await message_to_react.add_reaction(random.choice(list_of_emojis))

async def random_mention(message, args):
    for x in range(int(args[0])):
        await message.reply(random.choice(message.channel.members).mention)

async def flip_coin(message, args):
    for x in range(int(args[0])):
        await message.reply(random.choice(["heads", "tails"]))

async def roll_dice(message, args):
    nums = []
    for x in range(int(args[0])):
        nums.append(str(random.randint(1, int(args[1]))) + " ")
    await message.reply("The results are: " + ''.join(nums))


async def confuse(message, args):
    args_with_spaces = args
    for arg_num, arg in enumerate(args):
        args_with_spaces[arg_num] = arg + ' '

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": ""},
            {"role": "user", "content": "generate random, nonsensical message"}
        ]
    )

    await message.reply(completion.choices[0].message.content)

async def say_in_channel(message, args):
    args_with_spaces = args
    for arg_num, arg in enumerate(args):
        args_with_spaces[arg_num] = arg + ' '

    await message.channel_mentions[0].send(''.join(args_with_spaces[:len(args_with_spaces)-1]))
    await message.delete()

@trusted_role_command
async def delete_channel(message, args):
    await message.channel_mentions[0].delete()

@trusted_role_command
async def delete_all(message, args):
    for channel in message.guild.text_channels:
        if channel.name == args[0]:
            try:
                await channel.delete()
            except:
                pass

@trusted_role_command
async def create_channel(message, args):
    for category in message.guild.categories:
        if category.name == args[1]:
            await message.guild.create_text_channel(args[0], category=category)

async def set_trusted_role(message, args):
    if message.author == message.guild.owner:
        try:
            with open('trusted_roles', 'rb') as trusted_roles:
                loaded_trusted_roles = pickle.load(trusted_roles)
        except EOFError:
            loaded_trusted_roles = {}
        loaded_trusted_roles[str(message.guild.id)] = message.role_mentions[0].id
        with open('trusted_roles', 'wb') as trusted_roles:
            pickle.dump(loaded_trusted_roles, trusted_roles)
    else:
        await message.channel.send("No permissions")

@trusted_role_command
async def kick(message, args):
    await message.mentions[0].kick()

@trusted_role_command
async def ban(message, args):
    await message.mentions[0].ban()

@trusted_role_command
async def give_roles(message, args):
    await message.mentions[0].add_roles(*message.role_mentions)

@trusted_role_command
async def remove_roles(message, args):
    await message.mentions[0].remove_roles(*message.role_mentions)

async def cat_command(message, args):
    await message.channel.send(json.loads(requests.get('https://api.thecatapi.com/v1/images/search?size=full').text)["url"])

commands = {
    "amogus": amogus,
    "say": hardcore_says,
    "help": hardcore_helps,
    "random_reaction": random_reaction,
    "random_mention": random_mention,
    "flip_coin": flip_coin,
    "roll_dice": roll_dice,
    "say_in_channel": say_in_channel,
    "delete_channel": delete_channel,
    "delete_all": delete_all,
    "create_channel": create_channel,
    "set_trusted_role": set_trusted_role,
    "kick": kick,
    "ban": ban,
    "confuse": confuse,
    "give_roles": give_roles,
    "remove_roles": remove_roles,
    "cat": cat_command
}

token = open("token.txt", "r").read()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user.display_name}')
    await bot.change_presence(activity=discord.Activity(buttons=[{"label": "L", "url": "javascript:alert(1)"}]))

@bot.event
async def on_message(message):
    insult_triggers = ("I'm best!", "I'm best.", "I'm best", "I'm the best!", "I'm the best.", "I'm the best", "I am best!", "I am best.", "I am best", "I'm amazing!", "I'm amazing.", "I'm amazing", "I am amazing!", "I am amazing.", "I am amazing")
    if message.content.startswith('Hardcore '):
        command_args = message.content.split()
        command_name = command_args[1]
        del command_args[0:2]
        try:
            await commands[command_name](message, command_args)
        except KeyError:
            await message.reply(f"Command {command_name} doesn't exist")
    elif message.content in insult_triggers:
        await message.reply("No, you are not.")

async def reconnect_loop():
    while True:
        await asyncio.sleep(1)
        if bot.is_closed():
            print('Bot is disconnected, attempting to reconnect...')
            try:
                await bot.start(token)
                print('Reconnect successful.')
                break
            except Exception as e:
                print(f'Reconnect failed, {e}, retrying in 5 seconds...')
                await asyncio.sleep(5)

async def main():
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Fatal exception {e}, running reconnect loop.")
        await reconnect_loop()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
