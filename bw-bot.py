#discord.py API - http://discordpy.readthedocs.io/en/latest/api.html
import discord
import asyncio
from discord.ext.commands import Bot
from discord.ext import commands
import platform
import re
import bw_bot_private

client = Bot(description="BW Bot", command_prefix="~", pm_help = False)

# Returns true if the role is able to be used by the average user
def able_to_modify_role(role):
        permissions = role.permissions
        return not (role.is_everyone
                    or permissions.kick_members
                    or permissions.ban_members
                    or permissions.administrator
                    or permissions.manage_channels
                    or permissions.manage_server
                    or permissions.view_audit_logs
                    or permissions.manage_nicknames
                    or permissions.manage_roles
                    or permissions.manage_webhooks)

# Returns true if the user is able to join the role (Role position lower than highest user role position)
def low_enough_role(user, role):
        highest_position = 0
        for user_role in user.roles:
                highest_position = max(user_role.position, highest_position)

        return highest_position >= role.position

class bot_command:
        def is_private(self):
                return False
        # Returns the command string which is associated with this object
        def get_command(self):
                return ""
        # Handles the argument if the command is valid
        async def handle(self, client, message, member, command, argument):
                pass

# Creates role in server
class create_role(bot_command):
        def get_command(self):
                return "createrole"
        async def handle(self, client, message, member, command, argument):
                if discord.utils.get(message.server.roles, name=argument) == None:
                        await client.create_role(message.server, name=argument, mentionable=True)
                        await client.send_message(message.channel, member.mention + " you created the role '" + argument + "'")
                else:
                        await client.send_message(message.channel, "The role '" + argument + "' already exists")

# Adds role to user
class add_role(bot_command):
        def get_command(self):
                return "addrole"
        async def handle(self, client, message, member, command, argument):
                role = discord.utils.get(message.server.roles, name=argument)
                
                if role != None:
                        if low_enough_role(member, role):
                                await client.add_roles(member, role)
                                await client.send_message(message.channel, member.mention + " you have been added to role '" + role.name + "'")
                        else:
                                await client.send_message(message.channel, member.mention + " you cannot join desired role as for you have too low permissions")
                else:
                        await client.send_message(message.channel, "Role '" + argument + "' does not exist. Roles are case-sensitive")

# Removes role from user
class remove_role(bot_command):
        def get_command(self):
                return "removerole"
        async def handle(self, client, message, member, command, argument):
                role = discord.utils.get(message.server.roles, name=argument)
                if role != None:
                        if low_enough_role(member, role):
                                await client.remove_roles(member, role)
                                await client.send_message(message.channel, member.mention + " you have been removed from role '" + role.name + "'")
                        else:
                                await client.send_message(message.channel, member.mention + " you cannot leave role as for you have too low permissions")
                else:
                        await client.send_message(message.channel, "You do not have role '" + argument + "' Roles are case-sensitive")

# Prints all the avaliable roles to chat
class roles(bot_command):
        def get_command(self):
                return "roles"
        async def handle(self, client, message, member, command, argument):
                all_roles = message.server.roles

                roles_pretty = "All Roles:\n```"
                for role in all_roles:
                        if able_to_modify_role(role):
                                roles_pretty += role.name + "\n"
                roles_pretty += "```"
                await client.send_message(message.channel, roles_pretty)

# Returns help regarding the bot
class bot_help(bot_command):
        def get_command(self):
                return "help"
        async def handle(self, client, message, member, command, argument):
                await client.send_message(message.channel, "\
Bourbon-Bot is a custom made bot for Bourbon Warfare. The bot is used as a helper for \
members to easily do things that admins may be too busy for. To use Bourbon Bot, \
type `@bourbon-bot [command] [argument]` replacing `[` and `]` respectively. Type \
`@bourbon-bot commands` to list all commands.\
")

# Lists all bot commands
class commands(bot_command):
        def __init__(self, command_list):
                self.all_commands = command_list
                
        def get_command(self):
                return "commands"
        async def handle(self, client, message, member, command, argument):
                pretty_commands = "All Commands: ```\n"
                for obj_command in self.all_commands:
                        if not obj_command.is_private():
                                pretty_commands += obj_command.get_command() + "\n"
                pretty_commands += "```"
                await client.send_message(message.channel, pretty_commands)

class slackbot(bot_command):
        def is_private(self):
                return True
        def get_command(self):
                return "slackbot"
        async def handle(self, client, message, member, command, argument):
                await client.send_message(message.channel, "You're a Slackbot!")

class clean_roles(bot_command):
        def get_command(self):
                return "cleanroles"
        async def handle(self, client, message, member, command, argument):
                role_list = []
                for user in message.server.members:
                        role_list += user.roles
                role_list = list(set(role_list))

                delete_roles_pretty = "```Removed following roles:\n"
                for role in message.server.roles:
                        if role not in role_list:
                                if not low_enough_role(discord.utils.get(message.server.members, name=client.user.name), role):
                                        continue
                                if not able_to_modify_role(role):
                                        continue
                                delete_roles_pretty += role.name + "\n"
                                await client.delete_role(message.server, role)

                delete_roles_pretty += "```"

                await client.send_message(message.channel, delete_roles_pretty)
                        
                
# Add all possible commands to the command list
command_list = []
command_list += [create_role()]
command_list += [add_role()]
command_list += [remove_role()]
command_list += [roles()]
command_list += [bot_help()]
command_list += [commands(command_list)]
command_list += [slackbot()]
command_list += [clean_roles()]

### Bot message handling. Should not have to modify under this comment

@client.event
async def on_ready():
	print('Logged in as '+client.user.name+' (ID:'+client.user.id+') | Connected to '+str(len(client.servers))+' servers | Connected to '+str(len(set(client.get_all_members())))+' users')
	print('--------')
	print('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__, platform.python_version()))
	print('--------')
	print('Use this link to invite {}:'.format(client.user.name))
	print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=268435456'.format(client.user.id))
	print('--------')
	
	return await client.change_presence(game=discord.Game(name='Probably ARMA'))

@client.event
async def on_message(message):
        content = message.content.split()
        if len(content) < 2:
                return
        if re.sub("[^0-9]", "", content[0]) != client.user.id:
                # if the first "argument" in a message is not the bot we don't care about anything else
                return
        argument = ""
        member = message.author
        command = content[1]
        if len(content) >= 3:
                argument = content[2]
                role = discord.utils.get(message.server.roles, name=argument)
                if role != None:
                        if not low_enough_role(discord.utils.get(message.server.members, name=client.user.name), role):
                                # Error checking if the bot has permission to modify a role it is underneath
                                await client.send_message(message.channel, "Bot has too low permission to modify role '" + argument + "'")
                                return
                        if not able_to_modify_role(role):
                                # If the wanted argument is a role and the role can do anything that isn't user-created, we don't allow it
                                await client.send_message(message.channel, "Unable to modify role '" + argument + "'")
                                return

        found_command = False
        for command_obj in command_list:
                if command_obj.get_command() == command:
                        await command_obj.handle(client, message, member, command, argument)
                        found_command = True
                        break

        if not found_command:
                await client.send_message(message.channel, "Command `" + command + "` does not exist")
                

client.run(bw_bot_private.get_bot_token())
