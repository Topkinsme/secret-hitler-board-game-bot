#a bot by top

import discord
import logging
from discord.utils import get
from discord.ext import commands
from discord.ext import tasks
from discord.ext.commands import Bot
import asyncio
import random
import os
import time
import datetime
from datetime import date,timedelta
import json
import copy
import pymongo,dns
import keep_alive
import inspect
import textwrap
import io

token = str(os.environ.get("tokeno"))
dbpass=str(os.environ.get("dbpass"))

intents = discord.Intents.default()
intents.members = True
intents.presences = True


bot = commands.Bot(command_prefix = "!",intents=intents)
#bot.remove_command('help')
client = pymongo.MongoClient("mongodb+srv://Topkinsme:"+dbpass+"@top-cluster.x2y8s.mongodb.net/<dbname>?retryWrites=true&w=majority")
db = client.shbot
logging.basicConfig(level=logging.INFO)


@bot.event
async def on_ready():
    print("Working boi!")
    global annchannel
    global peochannel
    global lobby
    global data
    global userd
    global lastping
    global gamestate
    global starttime
    global logz
    lobby = bot.get_channel(754034408410972181)
    peochannel = bot.get_channel(706771948708823050)
    annchannel = bot.get_channel(760783052745080902)
    #no pls await lobby.send("Who's up for a game?! :smiley:")
    await annchannel.send("The bot is online!")
    await bot.change_presence(activity=discord.Game(name="Secret Hitler!", type=1))
    try:
        my_collection = db.main
        my_collection_t = db.user
        data = my_collection.find_one()
        userd=my_collection_t.find_one()
        gamestate = data['gamestate']
        '''with open('data.json','r') as f:
            data = json.load(f)
            print(data)'''
        gamestate=data['gamestate']
        lastping=None
        logz=commands.Paginator(prefix="",suffix="")
    except:
        print("Could not load the data")
        data={}
        data['signedup']={}
        data['players']={}
        data['gamestate']=0
        gamestate=data['gamestate']
        lastping=None
        data['deck']=[]
        data['playerorder']=[]
        data['roundno']=0
        data['liblaw']=0
        data['faclaw']=0
        data['power']={}
        data["card"]=""
        data['failcounter']=0
        data['dekk']=[]
        data['board']=0
        userd={}
        userd['users']={}
        await annchannel.send("The notif list has been erased!!!")
    if len(data['signedup'])>0 and gamestate==0:
        starttime=datetime.datetime.now()
        timeoutloop.start()

        

        
@bot.event
async def on_message(message): 
    global userd
    if message.author.id == 706771257256968243:
        return
    '''if message.channel.id!=754034408410972181:
        return'''
    if message.guild==None:
      await annchannel.send(f"<{message.author}> {message.content}")
    ath=str(message.author.id)
    if ath not in userd['users']:
      makeacc(ath)
    await bot.process_commands(message)   
    
  
@bot.event
async def on_member_join(member):
    await peochannel.send("{} has joined our server today! :tada: ".format(member.mention))
    await annchannel.send("{} has joined our server today! :tada: ".format(member.mention))
    await member.send("Thank you for joining Topkin's Secret H1tl0r Mini-game discord server. We gladly welcome you here.:smile: \n Before you play , do read the rules and what you need to know before you play the game. \n Have fun! :tada:")

    
@bot.event
async def on_member_remove(member):
    await annchannel.send("{} has left the server.".format(member.mention))
    ath=str(member.id)
    if ath in userd['users']:
      userd['users'].pop(ath)

@bot.event
async def on_reaction_add(reaction,user):
    #print(reaction)
    uid=user.id
    guildd=bot.get_guild(706761016041537539)
    role1 = discord.utils.get(guildd.roles, name="Players")
    if gamestate<1:
        return
    if user.id == 706771257256968243:
        return
    if role1 not in user.roles:
        await reaction.message.remove_reaction(reaction,user)  
    pass
    
    
@bot.event
async def on_command_error(ctx,error):
    await ctx.send(error)
    
@bot.event
async def on_message_delete(message):
    if message.author.id==450320950026567692:
      return
    await annchannel.send("{}'s message `{}` was deleted in <#{}>".format(message.author.name,message.content,message.channel.id))

@bot.event
async def on_user_update(before,after):
    global userd
    if before.name==after.name:
        return
    else:
        await annchannel.send("'{}' has changed thier name to '{}' .".format(before.name,after.name))
        ath=str(after.id)
        try:
          userd['users'][ath]['name']=after.name
        except:
          pass



#Game Master


@bot.command()
@commands.has_role("Admin")
async def pdata(ctx):
    '''Send the complete data file. <Game master>'''
    print(data)
    await ctx.send(data)

@bot.command()
@commands.has_role("Admin")
async def puserd(ctx):
    '''Send the complete data file. <Game master>'''
    print(userd)
    await ctx.send(userd)

@bot.command(hidden=True)
@commands.has_role("Admin")
async def sudo(ctx,who: discord.User, *, command: str):
        """Run a command as another user optionally in another channel."""
        msg = copy.copy(ctx.message)
        channel = ctx.channel
        msg.channel = channel
        msg.author = channel.guild.get_member(who.id) or who
        msg.content = ctx.prefix + command
        new_ctx = await bot.get_context(msg, cls=type(ctx))
        #new_ctx._db = ctx._db
        await bot.invoke(new_ctx)
    
@bot.command()
@commands.has_role("Admin")
async def logout(ctx):
    '''Logs out the bot'''
    await ctx.send("Logging out.")
    await bot.logout()

@bot.command()
@commands.has_role("Admin")
async def evall(ctx,*,thing:str):
    '''Eval command <Informer>'''
    #rdanny's
    env = {
            'bot': bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            #'_': self._last_result
        }

    env.update(globals())
    stdout = io.StringIO()
    if thing.startswith('```') and thing.endswith('```'):
            a = '\n'.join(thing.split('\n')[1:-1])
            thing = a.strip('` \n')
    to_compile = f'async def func():\n{textwrap.indent(thing, "  ")}'
    try:
            exec(to_compile, env)
    except Exception as e:
            await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')
    func = env['func']
    try:
        ret = await func()
    except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')
    else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                await ctx.send(f'```py\n{value}{ret}\n```')

    
@bot.command()
@commands.has_role("Game Master")
async def togglegame(ctx):
    '''Turns the bot on or off <Game master>'''
    global gamestate
    if gamestate == -1:
        await ctx.send("Games are now open!")
        gamestate=0
    elif gamestate==0:
        await ctx.send("Games are now closed!")
        gamestate = -1
    else:
        await ctx.send("A game is in progress. Please wait for it to finish.")
    data['gamestate']=gamestate
    dump()
    
@bot.command()
@commands.has_role("Game Master")
async def poll(ctx,*,message):
    '''Creates a poll <Game master>'''
    poll = discord.Embed(colour=discord.Colour.blurple())
    poll.set_author(name="POLL")
    poll.add_field(name="Reg:- ",value=message,inline="false")
    reac="\U0001f44d"
    reac2="\U0001f44e"
    reac3="⛔"
    a=await ctx.send(embed=poll)
    await a.add_reaction(reac)
    await a.add_reaction(reac2)
    await a.add_reaction(reac3)

@bot.command()
@commands.has_role("Game Master")
async def kick(ctx,member:discord.Member):
    await member.kick()
    await ctx.send("{} has been kicked from the server.".format(member.mention))

@bot.command()
@commands.has_role("Game Master")
async def ban(ctx,member:discord.Member):
    '''Allows to ban a user <Game master>'''
    await member.ban()
    await ctx.send("{} has been banned from the server.".format(member.mention))
    
@bot.command()
@commands.has_role("Admin")
async def compreset(ctx):
    '''Complete reset. <Game master>'''
    global data
    global gamestate
    global logz
    data={}
    data['signedup']={}
    data['players']={}
    data['gamestate']=0
    gamestate=0
    lastping=None
    data['deck']=[]
    data['playerorder']=[]
    data['roundno']=0
    data['liblaw']=0
    data['faclaw']=0
    data['failcounter']=0
    data['power']={}
    data["card"]=""
    data['dekk']=[]
    data['board']=0
    logz.clear()
    await ctx.send("A complete erasure of all data has been done.")
    dump()

@bot.command()
@commands.has_role("Game Master")
async def forceend(ctx):
    '''Use this command to force end the game.'''
    global data
    guildd=bot.get_guild(706761016041537539)
    role1 = discord.utils.get(guildd.roles, name="Players")
    role2 = discord.utils.get(guildd.roles, name="Dead")
    for ath in data['players']:
        userr=discord.utils.get(guildd.members,id=int(ath))
        await userr.remove_roles(role1)
        await userr.remove_roles(role2)
        
    chnl=discord.utils.get(guildd.channels,name="lobby")
    await chnl.set_permissions(guildd.default_role,read_messages=True,send_messages=True)
    chnl=discord.utils.get(guildd.channels,name="lobby")
    await chnl.set_permissions(role1,read_messages=True,send_messages=True)
    data={}
    data['signedup']={}
    data['players']={}
    data['gamestate']=0
    gamestate=0
    data['deck']=[]
    data['playerorder']=[]
    data['roundno']=0
    data['liblaw']=0
    data['faclaw']=0
    data['failcounter']=0
    data['power']={}
    data["card"]=""
    data['dekk']=[]
    data['board']=0
    logz.clear()
    await lobby.send("Game has been reset.")
    dump()


@bot.command(aliases=["^","pro"])
@commands.has_role("gm")
async def promote(ctx):
  '''To promote yourself. <Game Master>'''
  guildd=bot.get_guild(706761016041537539)
  role = discord.utils.get(guildd.roles, name="Game Master")
  ath = str(ctx.author.id)
  await ctx.author.add_roles(role)
  role = discord.utils.get(guildd.roles, name="gm")
  await ctx.author.remove_roles(role)
  await ctx.send("You have been promoted , {}".format(ctx.author.mention))

@bot.command(aliases=["v","dem"])
@commands.has_role("Game Master")
async def demote(ctx):
  '''To promote yourself. <Game Master>'''
  guildd=bot.get_guild(706761016041537539)
  role = discord.utils.get(guildd.roles, name="gm")
  ath = str(ctx.author.id)
  await ctx.author.add_roles(role)
  role = discord.utils.get(guildd.roles, name="Game Master")
  await ctx.author.remove_roles(role)
  await ctx.send("You have been demoted , {}".format(ctx.author.mention))

#all
@bot.command()
async def ping(ctx):
    '''Returns pong'''
    print("Pong!")
    await ctx.send("Pong!")
    dump()

@bot.command(aliases=["table"])
async def datatable(ctx):
  '''Use this to get a useful info table.'''
  await ctx.send("""__**Table-**__

**Role Distribution-**

Players   |     5    |     6    |     7    |     8    |     9     |   10
─────────────────────────────
Liberals  |     3    |     4    |     4    |     5    |     5    |     6
─────────────────────────────
Fascists  |  1+H  |  1+H  |  2+H  |  2+H  |  3+H  |  3+H

**Boards-**

Liberal Board - :black_circle::black_circle: :black_circle::black_circle::crown:

Fascist Board if 5-6 players -  :black_circle::black_circle::eye::dagger::dagger::crown:
Fascist Board if 7-8 players - :black_circle::mag::pen_ballpoint::dagger::dagger::crown:
Fascist Board if 9-10 players - :mag::mag::pen_ballpoint::dagger::dagger::crown:

**Powers-**

:eye:  - Allows the current president to look at the next three cards in order.
:mag:  - Allows the current president to look at the loyalty of a person. (Note that this will only tell the team, not the role.) 
:pen_ballpoint:  - Allows the current president to choose the next president.
:dagger:  - Allows the current president to kill a person from game.
:crown:  - Victory.""")
    
@bot.command(aliases=["notif"])
async def notifyme(ctx):
    '''Use this to add or remove yourself from the notify list.'''
    global data
    global userd
    guildd=bot.get_guild(706761016041537539)
    ath=str(ctx.author.id)
    if ath not in userd['users']:
      makeacc(ath)
    
    if userd['users'][ath]['notif']==0:
        userd['users'][ath]['notif']=1
        await ctx.send("You will now be notified when future games occur.")
    else:
        userd['users'][ath]['notif']=0
        await ctx.send("You will now **not** be notified when future games occur.")
    dump()

@bot.command()
@commands.has_role("Signed-Up")
async def notify(ctx):
    '''Use this to ping people who might be willing to play'''
    global lastping
    global data
    global userd
    guildd=bot.get_guild(706761016041537539)
    if lastping==None or datetime.datetime.now()-lastping>timedelta(minutes=30):
        lastping=datetime.datetime.now()
        msg= "{} is pinging! ".format(ctx.author.mention)
        for ath in userd['users']:
          if userd['users'][ath]['notif']==1:
            if ath not in data['signedup']:
              userr=discord.utils.get(guildd.members,id=int(ath))
              status=str(userr.status)
              if status=="online" or status=="idle" or status=="dnd":
                  msg+="<@{}> ".format(ath)
        await ctx.send(msg)
    else:
        await ctx.send("Please wait {} longer. The last ping was on {}.".format(timedelta(minutes=30)-(datetime.datetime.now()-lastping),lastping))
    dump()

@bot.command()
async def profile(ctx,user:discord.User=None):
    '''Use this to view someone's profile.'''
    if user == None:
      user=ctx.author
    url=user.avatar_url
    name=user.name
    user=str(user.id)
    if user not in userd['users']:
      makeacc(user)
    profile=discord.Embed(colour=discord.Colour.teal())
    profile.set_author(name="Profile-")
    profile.set_thumbnail(url=url)
    profile.add_field(name="Username-",value="{}".format(name),inline=False)
    profile.add_field(name="Games won to Games played-",value="{}/{}".format(userd['users'][user]['won'],userd['users'][user]['games']),inline=False)
    profile.add_field(name="Roles-",value="Times as lib - {} \nTimes as Fac - {} \nTimes as Hit - {}".format(userd['users'][user]['tlib'],userd['users'][user]['tfac'],userd['users'][user]['thit']),inline=False)
    profile.add_field(name="Wins-",value="Wins as lib - {} \nWins as Fac - {} \nWins by enacting 5 lib policies - {} \nWins by enacting 6 fac policies - {} \nWins by electing Hit - {} \nWins by assasinating Hit - {}".format(userd['users'][user]['wonl'],userd['users'][user]['wonf'],userd['users'][user]['wonle'],userd['users'][user]['wonfe'],userd['users'][user]['wonfhe'],userd['users'][user]['wonlk']),inline=False)
    if userd['users'][user]['notif']==0:
      text="0 - Notifications Off"
    elif userd['users'][user]['notif']==1:
      text="1 - Notifications On"
    profile.add_field(name="Notify Mode-",value=text,inline=False)
    await ctx.send(embed=profile)

    
@bot.command(aliases=["j","join"])
async def signup(ctx):
    '''Use this to join a game'''
    global data
    global gamestate
    global starttime
    if gamestate!=0:
        await ctx.send("Either games have been turned off or a game is currently in progress. Try again later.")
        return
    ath=str(ctx.author.id)
    if not ath in data['signedup']:
        if len(data['signedup'])>9:
            await ctx.send("Lobby at maximum capacity. Please try again later!")
            return
        if data['signedup']=={}:
          try:
            starttime=datetime.datetime.now()
            timeoutloop.start()
          except:
            pass
        data['signedup'][ath] = 0
        guildd=bot.get_guild(706761016041537539)
        role = discord.utils.get(guildd.roles, name="Signed-Up")
        await ctx.send("You have been signed-up! :thumbsup:")
        await ctx.author.add_roles(role)
        dump()
    else:
        data['signedup'].pop(ath)
        guildd=bot.get_guild(706761016041537539)
        role = discord.utils.get(guildd.roles, name="Signed-Up")
        await ctx.send("You have been signed-out!")
        await ctx.author.remove_roles(role)
        dump()            

        

@bot.command(aliases=["slist","sl"])
async def signeduplist(ctx):
    '''Tells you the number of people that have signed up'''
    msg = await ctx.send("Loading.")
    temp=""
    a=0
    for person in data['signedup']:
        temp+="<@{}> \n".format(person)
        a+=1
    temp+="The number of people who have signed up is- {}".format(a)
    await msg.edit(content=temp)

@bot.command(aliases=["vs"])
@commands.has_role("Signed-Up")
async def vstart(ctx):
    '''Vote to start the game <Signedup>'''
    global data
    global gamestate
    ath=str(ctx.author.id)
    if gamestate!=0:
        await ctx.send("Wrong gamestate.")
        return
    if len(data['signedup'])<5:
        await ctx.send("Wait for atleast 5 people to join.")
        return
    if data['signedup'][ath] == 1:
        data['signedup'][ath] = 0
        await ctx.send("Retracted your vote.")
    elif data['signedup'][ath] == 0:
        data['signedup'][ath] = 1
        await ctx.send("You've voted to start the game.")
        a=0
        b=0
        for ath in data['signedup']:
            if data['signedup'][ath] ==1:
                a+=1
            elif data['signedup'][ath] ==0:
                b+=1
        await ctx.send("{} out of {} people have voted to start the game.".format(a,a+b))
        if a>b and gamestate==0:
            await lobby.send("A game is starting , <@&706782757677826078>!")
            gamestate =1
            data['gamestate']=1
            await start()
    else:
        await ctx.send("You are currently not playing. Type !signup to join the game.")
    dump()


@bot.command(aliases=["t","so"])
async def time(ctx):
  '''Tells you how much time is left before the lobby expires.'''
  if len(data['signedup'])==0:
    await ctx.send("Lobby Empty.")
    return
  try:
    timeo = timedelta(minutes=30) -(datetime.datetime.now()-starttime)
    await ctx.send("{} time left before the lobby is timed out".format(timeo))
  except:
    await ctx.send("Lobby empty or a game is going on. Or there was a error.")

async def start():
    global data
    global gamestate
    global dekk
    global logz
    gamestate =1
    data['gamestate']=1
    playernum=0
    for ath in data['signedup']:
        guildd=bot.get_guild(706761016041537539)
        userr=discord.utils.get(guildd.members,id=int(ath))
        role = discord.utils.get(guildd.roles, name="Signed-Up")
        await userr.remove_roles(role)
        role = discord.utils.get(guildd.roles, name="Players")
        await userr.add_roles(role)
        playernum+=1
        data['players'][ath]={}
    role = discord.utils.get(guildd.roles, name="Players")
    chnl=discord.utils.get(guildd.channels,name="lobby")
    await chnl.set_permissions(role,read_messages=True,send_messages=True)
    roles=[]
    libn=0
    facn=0
    if playernum==5:
        libn=3
        facn=1
        data['board']=1
        logz.add_line("The game had 5 players.")
    elif playernum==6:
        libn=4
        facn=1
        data['board']=1
        logz.add_line("The game had 6 players.")
    elif playernum==7:
        libn=4
        facn=2
        data['board']=2
        logz.add_line("The game had 7 players.")
    elif playernum==8:
        libn=5
        facn=2
        data['board']=2
        logz.add_line("The game had 8 players.")
    elif playernum==9:
        libn=5
        facn=3
        data['board']=3
        logz.add_line("The game had 9 players.")
    elif playernum==10:
        libn=6
        facn=3
        data['board']=3
        logz.add_line("The game had 10 players.")
    listoplayers=[]
    rolelist=[]
    for a in range(libn):
        roles.append("Liberal")
    for a in range(facn):
        roles.append("Fascist")
    roles.append("Hitler")
    for player in data['players']:
        listoplayers.append(player)
        #print(listoplayers)
    for role in roles:
        rolelist.append(role)
        #print(listoplayers)
    countp=len(listoplayers)
    countr=len(rolelist)
    num=0
    facs=[]
    guildd=bot.get_guild(706761016041537539)
    while num<countp:
        user = random.choice(listoplayers)
        listoplayers.remove(user)
        role= random.choice(rolelist)
        rolelist.remove(role)
        data['players'][user]['role']=role
        data['players'][user]['checked']=0
        data['players'][user]['state']=1
        if data['players'][user]['role']=="Hitler":
            userr=discord.utils.get(guildd.members,id=int(user))
            hitler=userr.name
        elif data['players'][user]['role']=="Fascist":
            userr=discord.utils.get(guildd.members,id=int(user))
            facs.append(userr.name)
        #state 1 is alive ,0 is dead
        #print(data)
        num+=1
    players=[]
    for ath in data['players']:
        guildd=bot.get_guild(706761016041537539)
        userr=discord.utils.get(guildd.members,id=int(ath))
        roleinfo=discord.Embed(colour=discord.Colour.red())
        roleinfo.set_author(name="Role info!")
        roleinfo.add_field(name="This message has been sent to you to inform you of the role you have in the next up coming game in the Secret Hitler server!",value="**Your role for this game is `{}`!** \n You are **__not__** allowed to share this message! \n You are **__not__** allowed to share the screenshot of this message! \n Breaking any of these rules can result in you being banned from the server.".format(data['players'][ath]['role']),inline="false")
        if data['players'][ath]['role']=="Hitler":
            if playernum >6:
                a="Since this game has over 6 people , you will not not know who's on your team."
            else:
                people = ""
                for person in facs:
                    people += person + " "
                a="Your team consists of "+people
        elif data['players'][ath]['role']=="Fascist":
                a = "Your leader is "+hitler
                people = ""
                for person in facs:
                    people += person + " "
                a+=". Your team consists of "+people
        elif data['players'][ath]['role']=="Liberal":
            a="As a liberal, you do not know who your team mates are. Good luck."
        roleinfo.add_field(name=a,value="Have a good game!\n *I am a bot and this action has been done automatically. Please contact the Game Masters if anything is unclear.* ",inline="false")
        try:
            await userr.send(embed=roleinfo)
        except:
            print("Someone has blocked me")
        players.append(str(userr.id))
        logz.add_line("{} had the role {}".format(userr.mention,data['players'][ath]['role']))
    print(players)
    data['dekk']=['Liberal Policy','Liberal Policy','Liberal Policy','Liberal Policy','Liberal Policy','Liberal Policy','Fascist Policy','Fascist Policy','Fascist Policy','Fascist Policy','Fascist Policy','Fascist Policy','Fascist Policy','Fascist Policy','Fascist Policy','Fascist Policy','Fascist Policy']
    await drawdekk()
    random.shuffle(players)
    data['playerorder']=players
    print(data['playerorder'])
    data['roundno']=0
    dump()
    chnl=discord.utils.get(guildd.channels,name="lobby")
    await chnl.set_permissions(guildd.default_role,read_messages=True,send_messages=False)
    await round()
    dump()


async def round():
    global gamestate
    global data
    global canpass
    global prez
    global logz
    guildd=bot.get_guild(706761016041537539)
    gamestate =2
    data['gamestate']=2
    roundno=data['roundno']
    logz.add_line("--------------Round - {}".format(data['roundno']))
    if len(data['deck'])<3:
        await drawdekk()
    try:
      if canpass==2:
        ath=data['power']['prez']
        prez=discord.utils.get(guildd.members,id=int(ath))
        canpass=0
      else:
        try:
            ath=data['playerorder'][roundno]
            prez=discord.utils.get(guildd.members,id=int(ath))
            guildd=bot.get_guild(706761016041537539)
            data['power']['prez']=data['playerorder'][roundno]
            data['roundno']+=1
        except:
            data['roundno']=0
            roundno=0
            ath=data['playerorder'][roundno]
            prez=discord.utils.get(guildd.members,id=int(ath))
            guildd=bot.get_guild(706761016041537539)
            data['power']['prez']=data['playerorder'][roundno]
            data['roundno']+=1
    except:
        try:
            ath=data['playerorder'][roundno]
            prez=discord.utils.get(guildd.members,id=int(ath))
            guildd=bot.get_guild(706761016041537539)
            data['power']['prez']=data['playerorder'][roundno]
            data['roundno']+=1
        except:
            data['roundno']=0
            roundno=0
            ath=data['playerorder'][roundno]
            prez=discord.utils.get(guildd.members,id=int(ath))
            guildd=bot.get_guild(706761016041537539)
            data['power']['prez']=data['playerorder'][roundno]
            data['roundno']+=1
    effect=""
    if data['board']==1:
      if data['faclaw']==2:
        effect="**If a facist law is enacted, the president will get to see the next 3 cards.**"
    elif data['board']==2:
      if data['faclaw']==1:
        effect="**If a facist law is enacted, the president will get to check the loyalty of a person.**"
      elif data['faclaw']==2:
        effect="**If a facist law is enacted, the president will get to choose the next president.**"
    elif data['board']==3:
      if data['faclaw']==0:
        effect="**If a facist law is enacted, the president will get to check the loyalty of a person.**"
      elif data['faclaw']==1:
        effect="**If a facist law is enacted, the president will get to check the loyalty of a person.**"
      elif data['faclaw']==2:
        effect="**If a facist law is enacted, the president will get to choose the next president.**"
    if data['faclaw']==3 or data['faclaw']==4:
        effect="**If a facist law is enacted, the president will get the power to kill someone.**"
    elif data['faclaw']==5:
        effect="**If a facist law is enacted, the fascists will win.**"
    await lobby.send("Your president is {}. Please nominate a person using !nominate. \n {}".format(prez.mention,effect))
    logz.add_line("President was {}".format(prez.mention))
    dump()

@bot.command(aliases=["myr"])
@commands.has_role("Players")
async def myrole(ctx):
  '''Use this to make the bot send you your role.'''
  guildd=bot.get_guild(706761016041537539)
  playernum=0
  facs=[]
  for ath in data['signedup']:
      playernum+=1
      if data['players'][ath]['role']=="Hitler":
                userr=discord.utils.get(guildd.members,id=int(ath))
                hitler=userr.name
      elif data['players'][ath]['role']=="Fascist":
                userr=discord.utils.get(guildd.members,id=int(ath))
                facs.append(userr.name)
  ath=str(ctx.author.id)
  userr=discord.utils.get(guildd.members,id=int(ath))
  roleinfo=discord.Embed(colour=discord.Colour.red())
  roleinfo.set_author(name="Role info!")
  roleinfo.add_field(name="This message has been sent to you to inform you of the role you have in the next up coming game in the Secret Hitler server!",value="**Your role for this game is `{}`!** \n You are **__not__** allowed to share this message! \n You are **__not__** allowed to share the screenshot of this message! \n Breaking any of these rules can result in you being banned from the server.".format(data['players'][ath]['role']),inline="false")
  if data['players'][ath]['role']=="Hitler":
            if playernum >6:
                a="Since this game has over 6 people , you will not not know who's on your team."
            else:
                people = ""
                for person in facs:
                    people += person + " "
                a="Your team consists of "+people
  elif data['players'][ath]['role']=="Fascist":
                a = "Your leader is "+hitler
                people = ""
                for person in facs:
                    people += person + " "
                a+=". Your team consists of "+people
  elif data['players'][ath]['role']=="Liberal":
            a="As a liberal, you do not know who your team mates are. Good luck."
  else:
    a="-"
  roleinfo.add_field(name=a,value="Have a good game!\n *I am a bot and this action has been done automatically. Please contact the Game Masters if anything is unclear.* ",inline="false")
  try:
        await userr.send(embed=roleinfo)
        await ctx.send("I have sent you your role.")
  except:
        await ctx.send("You have blocked me or disabled dms.")



@bot.command(aliases=["nom","n"])
@commands.has_role("Players")
async def nominate(ctx,user:discord.Member):
    '''Use this to nominate someone to become chancellor <President>'''
    global data
    global gamestate
    global logz
    guildd=bot.get_guild(706761016041537539)
    if gamestate!=2:
        await ctx.send("It's not the right time.")
        return
    prath=data['power']['prez']
    prez=discord.utils.get(guildd.members,id=int(prath))
    if ctx.author.id!=prez.id:
        await ctx.send("You are not the president.")
        return
    if str(user.id) not in data['players']:
        await ctx.send("That person is not in the game.")
        return
    if data['players'][str(user.id)]['state']==0:
        await ctx.send("The person you chose is currently dead.")
        return
    if prez.id==user.id:
        await ctx.send("You cannot select yourselves.")
        return
    try:
        if user.id==int(data['power']['chan']):
            await ctx.send("The previous chancellor cannot be chancellor again.")
            return
        num=0
        for person in data['players']:
            if data['players'][person]['state']==1:
                num+=1
        if num>5:
            if user.id==int(data['power']['prez']):
                await ctx.send("If more than 5 people are alive , the previous president cannot be elected chancellor.")
                return
    except:
        #honestly fix this
        pass
    gamestate =3
    data['gamestate']=3
    msg = await lobby.send("The president has nominated {}! Please react to this message to cast your votes. You have 60 seconds.".format(user.mention))
    logz.add_line("{} was nominated.".format(user.mention))
    yes= "✅"
    no="❎"
    await msg.add_reaction(yes)
    await msg.add_reaction(no)
    await asyncio.sleep(60)
    ja=0
    nein=0
    channel=msg.channel
    msgid = msg.id
    msg = await channel.fetch_message(msgid)
    for reaction in msg.reactions:
        print(reaction)
        if str(reaction)==yes:
            ja+=reaction.count
        elif str(reaction)==no:
            nein+=reaction.count
    print(ja,nein)
    dump()
    if ja>nein:
        logz.add_line("{} was successfully elected.".format(user.mention))
        await lobby.send("{} has been elected as your chancellor!".format(user.mention))
        data['power']['chan']=str(user.id)
        if data['faclaw']>2 and data['players'][str(user.id)]['role']=="Hitler":
            await lobby.send("The game is now over! Hitler has become the chancellor!")
            logz.add_line("**GAME OVER - HITLER WAS ELECTED!**")
            await end("fhe")
            dump()
            return
        await legis()
    else:
        logz.add_line("{} was not elected.".format(user.mention))
        await fail()
    dump()
    

async def legis():
    global gamestate
    global data
    global logz
    gamestate =4
    data['gamestate']=4
    guildd=bot.get_guild(706761016041537539)
    role = discord.utils.get(guildd.roles, name="Players")
    chnl=discord.utils.get(guildd.channels,name="lobby")
    await chnl.set_permissions(role,read_messages=True,send_messages=False)
    user=data['power']['prez']
    userr=discord.utils.get(guildd.members,id=int(user))
    first = data['deck'].pop(0)
    second = data['deck'].pop(0)
    third = data['deck'].pop(0)
    msg = await userr.send("The next three cards in order are {} , {} and {}. React with A , B or C to get rid of the corresponding card. You have 20 seconds to choose. \n**PICK THE CARD YOU WANT TO DISCARD.**".format(first,second,third))
    logz.add_line("The president drew {},{},{}".format(first,second,third))
    one="\U0001f1e6"
    two="\U0001f1e7"
    three="\U0001f1e8"
    await msg.add_reaction(one)
    await msg.add_reaction(two)
    await msg.add_reaction(three)
    await asyncio.sleep(20)
    channel=msg.channel
    msgid = msg.id
    msg = await channel.fetch_message(msgid)
    fir=0
    sec=0
    tir=0
    for reaction in msg.reactions:
        if str(reaction)==one:
            fir+=reaction.count
        elif str(reaction)==two:
            sec+=reaction.count
        elif str(reaction)==three:
            tir+=reaction.count
    
    if fir>sec and fir>tir:
            throw=first
            keep=second+" and the "+third
            first="[Discarded]"
    elif sec>fir and sec>tir:
            throw=second
            keep=first+" and the "+third
            second="[Discarded]"
    else:
            throw=third
            keep=first+" and the "+second
            third="[Discarded]"
    await userr.send("Alright you are discarding a {} and passing the {}.".format(throw,keep))
    logz.add_line("The president discarded {}".format(throw))
    user=data['power']['chan']
    userr=discord.utils.get(guildd.members,id=int(user))
    msg = await userr.send("The next three cards in order are {} , {} and {}. React with A , B or C to get rid of the corresponding card. You have 20 seconds to choose. Do not select a discarded card.\n**PICK THE CARD YOU WANT TO DISCARD.**".format(first,second,third))
    one="\U0001f1e6"
    two="\U0001f1e7"
    three="\U0001f1e8"
    await msg.add_reaction(one)
    await msg.add_reaction(two)
    await msg.add_reaction(three)
    await asyncio.sleep(20)
    channel=msg.channel
    msgid = msg.id
    msg = await channel.fetch_message(msgid)
    fir=0
    sec=0
    tir=0
    for reaction in msg.reactions:
        if str(reaction)==one:
            fir+=reaction.count
        elif str(reaction)==two:
            sec+=reaction.count
        elif str(reaction)==three:
            tir+=reaction.count
    if fir>sec and fir>tir:
            if first=="[Discarded]":
                second="[Discarded]"
            else:
                first="[Discarded]"
    elif sec>fir and sec>tir:
            if second=="[Discarded]":
                third="[Discarded]"
            else:
                second="[Discarded]"
    else:
            if third=="[Discarded]":
                first="[Discarded]"
            else:
                third="[Discarded]"
            third="[Discarded]"
    if first!="[Discarded]":
        keep=first
        data['card']=first
    elif second!="[Discarded]":
        keep=second
        data['card']=second
    elif third!="[Discarded]":
        keep=third
        data['card']=third
    if data["faclaw"]>4:
        msg=await userr.send("Do you wish to veto this vote? You have 20 seconds to choose.")
        yes= "✅"
        no="❎"
        await msg.add_reaction(yes)
        await msg.add_reaction(no)
        await asyncio.sleep(20)
        ja=0
        nein=0
        channel=msg.channel
        msgid = msg.id
        msg = await channel.fetch_message(msgid)
        for reaction in msg.reactions:
            print(reaction)
            if str(reaction)==yes:
                ja+=reaction.count
            elif str(reaction)==no:
                nein+=reaction.count
        await userr.send("Alright.")
        if ja>nein:
            user=data['power']['prez']
            userr=discord.utils.get(guildd.members,id=int(user))
            msg=await userr.send("Do you wish to veto this vote? The chancellor has requested to veto this vote. You have 20 seconds to choose.")
            yes= "✅"
            no="❎"
            await msg.add_reaction(yes)
            await msg.add_reaction(no)
            await asyncio.sleep(20)
            ja=0
            nein=0
            channel=msg.channel
            msgid = msg.id
            msg = await channel.fetch_message(msgid)
            for reaction in msg.reactions:
                print(reaction)
                if str(reaction)==yes:
                    ja+=reaction.count
                elif str(reaction)==no:
                    nein+=reaction.count
            if ja>nein:
                await lobby.send("The government has decided to veto this agenda.")
                logz.add_line("The government has decided to veto this agenda.")
                await fail()
                return
            else:
                await lobby.send("The chancellor wanted to veto this agenda but the president didn't agree.")
                logz.add_line("The chancellor wanted to veto this agenda but the president didn't agree.")
        else:
            await lobby.send("The chancellor did not want to veto this agenda.")
            logz.add_line("The chancellor did not want to veto this agenda.")
    await userr.send("Alright you are passing a {}.".format(keep)) 
    logz.add_line("The chancellor passed a {}".format(keep))
    data['failcounter']=0       
    await picked()
    dump()

async def picked():
    global gamestate
    global data
    global cankill
    global cancheck
    global canpass
    guildd=bot.get_guild(706761016041537539)
    role = discord.utils.get(guildd.roles, name="Players")
    chnl=discord.utils.get(guildd.channels,name="lobby")
    await chnl.set_permissions(role,read_messages=True,send_messages=True)
    gamestate =5
    data['gamestate']=5
    await winchecks()
    if cankill==1 or cancheck==1 or canpass==1:
        await lobby.send("The game will continue when the president does something.")
        while cankill==1:
            await asyncio.sleep(5)
        while cancheck==1:
            await asyncio.sleep(5)
        while canpass==1:
            await asyncio.sleep(5)
    await asyncio.sleep(5)
    if gamestate!=5:
      return
    else:
      await lobby.send("You have 20 seconds to discuss before the next round starts.")
      await asyncio.sleep(20)
      await lobby.send("Time for next round!")
      await round()
    dump()

@bot.command()
@commands.has_role("Players")
async def kill(ctx,user:discord.Member):
    '''Use this to kill the person'''
    global data
    global gamestate
    global cankill
    global logz
    guildd=bot.get_guild(706761016041537539)
    if gamestate!=5:
        await ctx.send("It's not the right time.")
        return
    if cankill==0:
        await ctx.send("You cannot kill.")
        return
    prath=data['power']['prez']
    prez=discord.utils.get(guildd.members,id=int(prath))
    if ctx.author.id!=prez.id:
        await ctx.send("You are not the president.")
        return
    if str(user.id) not in data['players']:
        await ctx.send("That person is not in the game.")
        return
    if data['players'][str(user.id)]['state']==0:
        await ctx.send("The person you chose is currently dead.")
        return
    if prez.id==user.id:
        await ctx.send("You cannot select yourselves.")
        return
    await lobby.send("The president has chosen {} to die.".format(user.mention))
    logz.add_line("The president chose {} to die.".format(user.mention))
    data['players'][str(user.id)]['state']=0
    num = data['playerorder'].index(str(user.id))
    if num<data['roundno']:
      data['roundno']-=1
    data['playerorder'].remove(str(user.id))
    role = discord.utils.get(guildd.roles, name="Players")
    await user.remove_roles(role)
    role = discord.utils.get(guildd.roles, name="Dead")
    await user.add_roles(role)
    if data['players'][str(user.id)]['role']=="Hitler":
        gamestate =6
        data['gamestate']=6
        await lobby.send("Congrats! The liberals have won! They have eliminated hitler!")
        logz.add_line("**GAME OVER - HITLER HAS BEEN KILLED.**")
        await end("lk")
        return
        dump()
    else:
        await lobby.send("That person was not the secret hitler.")
    cankill=0
    dump()
        
@bot.command()
@commands.has_role("Players")
async def check(ctx,user:discord.Member):
    '''Use this to check the person'''
    global data
    global gamestate
    global cancheck
    global logz
    guildd=bot.get_guild(706761016041537539)
    if gamestate!=5:
        await ctx.send("It's not the right time.")
        return
    if cancheck==0:
        await ctx.send("You cannot check.")
        return
    prath=data['power']['prez']
    prez=discord.utils.get(guildd.members,id=int(prath))
    if ctx.author.id!=prez.id:
        await ctx.send("You are not the president.")
        return
    if str(user.id) not in data['players']:
        await ctx.send("That person is not in the game.")
        return
    if data['players'][str(user.id)]['state']==0:
        await ctx.send("The person you chose is currently dead.")
        return
    if prez.id==user.id:
        await ctx.send("You cannot select yourselves.")
        return
    if data['players'][str(user.id)]['checked']==1:
        await ctx.send("That person has already been checked.")
        return
    cancheck=0
    data['players'][str(user.id)]['checked']=1
    await lobby.send("The president has chosen to check {}.".format(user.mention))
    logz.add_line("The president chose {} to check.".format(user.mention))
    ath=str(user.id)
    if data['players'][ath]['role']=="Libral":
      say="Libral"
    else:
      say="Fascist"
    await ctx.author.send("The person you checked is of loyalty {}.".format(say))
    dump()

@bot.command()
@commands.has_role("Players")
async def passprez(ctx,user:discord.Member):
    '''Use this to pass the presidentship to a person'''
    global data
    global gamestate
    global canpass
    global logz
    guildd=bot.get_guild(706761016041537539)
    if gamestate!=5:
        await ctx.send("It's not the right time.")
        return
    if canpass==0:
        await ctx.send("You cannot pass.")
        return
    prath=data['power']['prez']
    prez=discord.utils.get(guildd.members,id=int(prath))
    if ctx.author.id!=prez.id:
        await ctx.send("You are not the president.")
        return
    if str(user.id) not in data['players']:
        await ctx.send("That person is not in the game.")
        return
    if data['players'][str(user.id)]['state']==0:
        await ctx.send("The person you chose is currently dead.")
        return
    if prez.id==user.id:
        await ctx.send("You cannot select yourselves.")
        return
    await lobby.send("The president has chosen {} as the next president. Please wait a few seconds and the next round will start.".format(user.mention))
    logz.add_line("The president chose {} to be the next president.".format(user.mention))
    id=user.id
    data['power']['prez']=str(id)
    canpass=2
    dump()

async def fail():
    global data
    global logz
    await lobby.send("The government has failed!")
    data['failcounter']+=1
    if data['failcounter']>2:
        await lobby.send("The government has failed thrice.")
        logz.add_line("The government had failed thrice.")
        logz.add_line("There are {} Liberal policies and {} Fascist policies.".format(data['liblaw'],data['faclaw']))
        nexkt=data['deck'][0]
        data['deck'].pop(0)
        if nexkt=="Liberal Policy":
            data['dekk'].remove('Liberal Policy')
        elif nexkt=="Fascist Policy":
            data['dekk'].remove('Fascist Policy')
        data['card']=nexkt
        await winchecks()
        data['failcounter']=0
    await board(lobby)
    await lobby.send("You have 20 seconds to discuss before the next round starts.")
    await asyncio.sleep(20)
    await lobby.send("Time for next round!")
    await round()
    dump()
    
async def winchecks():
    global gamestate
    global data
    global cankill
    global cancheck
    global canpass
    global logz
    cankill=0
    cancheck=0
    canpass=0
    guildd=bot.get_guild(706761016041537539)
    if data['card']=="Liberal Policy":
        await lobby.send("A liberal law was passed!")
        data['dekk'].remove('Liberal Policy')
        data['liblaw']+=1
        if data['liblaw']>4:
            gamestate =6
            data['gamestate']=6
            await lobby.send("Congrats! The liberals have won!")
            logz.add_line("**GAME OVER - Liberals have passed 5 policies.**")
            await end("le")
            return
            dump()
    elif data['card']=="Fascist Policy":
        await lobby.send("A Fascist law was passed!")
        data['dekk'].remove('Fascist Policy')
        data['faclaw']+=1
        #addchecks for fail counter
        if data['faclaw']>5:
            gamestate =6
            data['gamestate']=6
            await lobby.send("Congrats! The Fascists have won!")
            logz.add_line("**GAME OVER - Fascists have passed 6 policies.**")
            await end("fe")
            return
            dump()
        elif data['faclaw']==1:
          if data['failcounter']==3:
            return
          if data['board']==3:
            await lobby.send("One Fascist law have been passed! The previous president can check the loyalty of a person in game")
            user=data['power']['prez']
            userr=discord.utils.get(guildd.members,id=int(user))
            await userr.send("Use !check to check the person.")
            cancheck=1
        elif data['faclaw']==2:
          if data['failcounter']==3:
            return
          if data['board']==3 or data['board']==2:
            await lobby.send("Two Fascist laws have been passed! The previous president can check the loyalty of a person in game")
            user=data['power']['prez']
            userr=discord.utils.get(guildd.members,id=int(user))
            await userr.send("Use !check to check the person.")
            cancheck=1
        elif data['faclaw']==3:
          if data['failcounter']==3:
            return
          if data['board']==1:
            await lobby.send("Three Fascist laws have been passed! The previous president has been shown the next three cards.")
            user=data['power']['prez']
            userr=discord.utils.get(guildd.members,id=int(user))
            if len(data['deck'])<3:
                await drawdekk()
            first = data['deck'][0]
            second = data['deck'][1]
            third = data['deck'][2]
            await userr.send("The next three cards in order are {} , {} and {}. You can do anything you want with this information BUT you are not allowed to copy paste this message.".format(first,second,third))
          elif data['board']==2 or data['board']==3:
            await lobby.send("Three Fascist laws have been passed! The previous president can choose the next president.")
            user=data['power']['prez']
            userr=discord.utils.get(guildd.members,id=int(user))
            await userr.send("Use !passprez to pass the presidency to a person.")
            canpass=1
        elif data['faclaw']==4:
            if data['failcounter']==3:
              return
            await lobby.send("Four Fascist laws have been passed! The previous president has the power to kill someone.")
            user=data['power']['prez']
            userr=discord.utils.get(guildd.members,id=int(user))
            await userr.send("Use !kill to kill a person.")
            cankill=1
        elif data['faclaw']==5:
            if data['failcounter']==3:
              return
            await lobby.send("Five Fascist laws have been passed! The previous president has the power to kill someone. Veto power has been unlocked.")
            user=data['power']['prez']
            userr=discord.utils.get(guildd.members,id=int(user))
            await userr.send("Use !kill to kill a person.")
            cankill=1
    await board(lobby)
    logz.add_line("There are {} Liberal policies and {} Fascist policies.".format(data['liblaw'],data['faclaw']))
    dump()

async def end(who):
    global data
    global userd
    global gamestate
    global logz
    win="The winners are-\n"
    lose="The people who didn't win are-\n"
    if who=="le":
        for ath in data['players']:
            userd['users'][ath]['games']+=1
            if data['players'][ath]['role']=="Liberal":
                win+="<@{}>\n".format(ath)
                userd['users'][ath]['won']+=1
                userd['users'][ath]['wonl']+=1
                userd['users'][ath]['wonle']+=1
            else:
                lose+="<@{}>\n".format(ath)
    elif who=="fe":
        for ath in data['players']:
            userd['users'][ath]['games']+=1
            if data['players'][ath]['role']=="Liberal":
                lose+="<@{}>\n".format(ath)
            else:
                win+="<@{}>\n".format(ath)
                userd['users'][ath]['won']+=1
                userd['users'][ath]['wonf']+=1
                userd['users'][ath]['wonfe']+=1
    elif who=="lk":
        for ath in data['players']:
            userd['users'][ath]['games']+=1
            if data['players'][ath]['role']=="Liberal":
                win+="<@{}>\n".format(ath)
                userd['users'][ath]['won']+=1
                userd['users'][ath]['wonl']+=1
                userd['users'][ath]['wonlk']+=1
            else:
                lose+="<@{}>\n".format(ath)
    elif who=="fhe":
        for ath in data['players']:
            userd['users'][ath]['games']+=1
            if data['players'][ath]['role']=="Liberal":
                lose+="<@{}>\n".format(ath)
            else:
                win+="<@{}>\n".format(ath)
                userd['users'][ath]['won']+=1
                userd['users'][ath]['wonf']+=1
                userd['users'][ath]['wonfhe']+=1
    for ath in data['players']:
      if data['players'][ath]['role']=="Liberal":
        userd['users'][ath]['tlib']+=1
      elif data['players'][ath]['role']=="Fascist":
        userd['users'][ath]['tfac']+=1
      elif data['players'][ath]['role']=="Hitler": 
        userd['users'][ath]['thit']+=1
    await lobby.send("{} \n\n {}".format(win,lose))
    await annchannel.send("{} \n\n {}".format(win,lose))
    log="-\nThe game went like this-\n\n"
    '''for a in data['logz']:
      log+=a
      log+="\n"
    if len(log)>2000:
      await lobby.send(log[:2000])
      await annchannel.send(log[:2000])
      await lobby.send(log[2000:])
      await annchannel.send(log[2000:])
    else:
      await lobby.send(log)
      await annchannel.send(log)'''
    for page in logz.pages:
      await lobby.send(page)
      await annchannel.send(page)
    guildd=bot.get_guild(706761016041537539)
    role1 = discord.utils.get(guildd.roles, name="Players")
    role2 = discord.utils.get(guildd.roles, name="Dead")
    for ath in data['players']:
        userr=discord.utils.get(guildd.members,id=int(ath))
        await userr.remove_roles(role1)
        await userr.remove_roles(role2)
        name = userr.name
        if len(name)>25:
          name=name[:25]
        name+=" [{}/{}]".format(userd['users'][ath]['won'],userd['users'][ath]['games'])
        try:
          await userr.edit(nick=name)
        except:
          pass
    chnl=discord.utils.get(guildd.channels,name="lobby")
    await chnl.set_permissions(guildd.default_role,read_messages=True,send_messages=True)
    chnl=discord.utils.get(guildd.channels,name="lobby")
    await chnl.set_permissions(role1,read_messages=True,send_messages=True)
    data={}
    data['signedup']={}
    data['players']={}
    data['gamestate']=0
    gamestate=0
    data['deck']=[]
    data['playerorder']=[]
    data['roundno']=0
    data['liblaw']=0
    data['faclaw']=0
    data['failcounter']=0
    data['power']={}
    data["card"]=""
    data['dekk']=[]
    data['board']=0
    logz.clear()
    await lobby.send("Game has been reset")
    dump()
    
async def drawdekk():
    global data
    global logz
    print(data['deck'])
    print(data['dekk'])
    data['deck']=[]
    num = random.randint(1, 15)
    for a in range(num):
      random.shuffle(data['dekk'])
    data['deck']=copy.deepcopy(data['dekk'])
    await lobby.send("A new deck has been formed.")
    logz.add_line("A new deck was formed. It was - ")
    temp=""
    for itemm in data['deck']:
      temp+=itemm
      temp+=" "
    logz.add_line(temp)
    dump()
    
async def board(chnl):
    board=discord.Embed(colour=discord.Colour.gold())
    board.set_author(name="The board currently looks like this!")
    liblawn="Cards - "
    faclawn="Cards - "
    failc="Count - "
    for a in range(data['liblaw']):
        liblawn+=":blue_square:"
    for a in range(data['faclaw']):
        faclawn+=":red_square:"
    for a in range(data['failcounter']):
        failc+=":white_circle:"
    board.add_field(name="Liberal Laws- (5 needed to win)",value=liblawn,inline="false")
    board.add_field(name="Liberal Powers-",value="Powers- :black_circle::black_circle: :black_circle::black_circle::crown:",inline="false")
    board.add_field(name="Fascist laws- (6 needed to win)",value=faclawn,inline="false")
    powers="Powers- "
    if data['board']==1:
      powers+=":black_circle::black_circle::eye::dagger::dagger::crown: "
    elif data['board']==2:
      powers+=":black_circle::mag::pen_ballpoint::dagger::dagger::crown: "
    elif data['board']==3:
      powers+=":mag::mag::pen_ballpoint::dagger::dagger::crown: "
    else:
      powers+=":black_circle::black_circle::eye::dagger::dagger::crown: "
    board.add_field(name="Fascist powers-",value=powers,inline="false")
    board.add_field(name="Fail counter- ",value=failc,inline="false")
    await chnl.send(embed=board)


@tasks.loop(seconds=60)
async def timeoutloop():
    global starttime
    global data
    global gamestate
    if data['signedup']=={}:
        timeoutloop.stop()
        print("Lobby empty")
    if gamestate>0:
        timeoutloop.stop()
    if datetime.datetime.now()-starttime>timedelta(minutes=30):
        await lobby.send("<@&706782757677826078>, the game has taken too long to start and cancelled. Type !j if you still want to play.")
        for ath in data['signedup']:
            guildd=bot.get_guild(706761016041537539)
            role = discord.utils.get(guildd.roles, name="Signed-Up")
            userr=discord.utils.get(guildd.members,id=int(ath))
            await userr.remove_roles(role)
        data['signedup']={}
        timeoutloop.stop()
        dump()
    #starttime+=1
    

    
'''async def timeout(ctx):
    return
    global start
    start = datetime.datetime.now()
    while True:
        if datetime.datetime.now()-start>timedelta(minutes=1):
            await lobby.send("<@&706782757677826078>, the game has taken too long to start and calcelled. Type !j if you still want to play.")
            for ath in data['signedup']:
                data['signedup'].pop(ath)
                guildd=bot.get_guild(706761016041537539)
                role = discord.utils.get(guildd.roles, name="Signed-Up")
                await ctx.send("You have been signed-out!")
                await ctx.author.remove_roles(role)
            break'''

@bot.command(aliases=["board","db"])
async def displayboard(ctx):
    '''Use this to display the board'''
    await board(ctx.channel)

@bot.command(aliases=["players","p"])
async def playerorder(ctx):
    '''Use this to display the player order'''
    msg = await ctx.send("Loading.")
    temp=""
    a=0
    temp+="The player order is \n"
    for person in data['playerorder']:
        temp+="<@{}> \n".format(person)
        a+=1
    await msg.edit(content=temp)

@bot.command()
async def cards(ctx):
  '''Tells you the number of cards you can see.'''
  if gamestate<1:
    ndeck=17
    ndiscard=0
    nboard=0
  else:
    ndeck=len(data['deck'])
    nboard=data['liblaw']+data['faclaw']
    ndiscard= 17 -(ndeck+nboard)
  await ctx.send("`{}` cards are in the pile , `{}` on the board and `{}` in the discard pile.".format(ndeck,nboard,ndiscard))

def makeacc(ath):
      global userd
      guildd=bot.get_guild(706761016041537539)
      userr=discord.utils.get(guildd.members,id=int(ath))
      if userr.bot ==True:
        return
      userd['users'][ath]={}
      userd['users'][ath]['name'] = userr.name
      userd['users'][ath]['tlib'] = 0
      userd['users'][ath]['tfac']= 0 
      userd['users'][ath]['thit']= 0
      userd['users'][ath]['games']= 0
      userd['users'][ath]['won']= 0
      userd['users'][ath]['wonl']= 0
      userd['users'][ath]['wonf']= 0
      userd['users'][ath]['wonle']= 0
      userd['users'][ath]['wonlk']= 0
      userd['users'][ath]['wonfe']= 0
      userd['users'][ath]['wonfhe']= 0
      userd['users'][ath]['notif']=0
      dump()

def dump():
    my_collection = db.main
    my_collection_t = db.user
    my_collection.drop()
    my_collection.insert_one(data)
    my_collection_t.drop()
    my_collection_t.insert_one(userd)
    '''with open('data.json', 'w+') as f:
        json.dump(data, f)'''

keep_alive.keep_alive()
bot.run(token)

