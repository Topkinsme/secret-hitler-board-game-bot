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

token = str(os.environ.get("tokeno"))
dbpass=str(os.environ.get("dbpass"))


bot = commands.Bot(command_prefix = "!")
#bot.remove_command('help')
client = pymongo.MongoClient("mongodb+srv://Topkinsme:"+dbpass+"@top-cluster.x2y8s.mongodb.net/<dbname>?retryWrites=true&w=majority")
db = client.shbot

@bot.event
async def on_ready():
    print("Working boi!")
    global annchannel
    global lobby
    global data
    global lastping
    global gamestate
    lobby = bot.get_channel(754034408410972181)
    annchannel = bot.get_channel(706771948708823050)
    await lobby.send("Who's up for a game?! :smiley:")
    await bot.change_presence(activity=discord.Game(name="Secret Hitler!", type=1))
    try:
        my_collection = db.main
        data = my_collection.find_one()
        gamestate = data['gamestate']
        '''with open('data.json','r') as f:
            data = json.load(f)
            print(data)'''
        gamestate=data['gamestate']
        lastping=None
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
        

        
@bot.event
async def on_message(message): 
    if message.author.id == 706771257256968243:
        return
    '''if message.channel.id!=754034408410972181:
        return'''
    await bot.process_commands(message)   
    
  
@bot.event
async def on_member_join(member):
    await annchannel.send("{} has joined our server today! :tada: ".format(member.mention))
    await member.send("Thank you for joining Topkin's Secret Hitler Mini-game discord server. We gladly welcome you here.:smile: \n\n Before you play , do read the rules and what you need to know before you play the game. \n\n Have fun! :tada:")
    
@bot.event
async def on_member_remove(member):
    await annchannel.send("{} has left the server.".format(member.mention))

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
    
#Game Master


@bot.command()
@commands.has_role("Game Master")
async def pdata(ctx):
    '''Send the complete data file. <Game master>'''
    print(data)
    await ctx.send(data)

@bot.command(hidden=True)
@commands.has_role("Game Master")
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
@commands.has_role("Game Master")
async def logout(ctx):
    '''Logs out the bot'''
    await ctx.send("Logging out.")
    await bot.logout()
    
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
@commands.has_role("Game Master")
async def compreset(ctx):
    '''Complete reset. <Game master>'''
    global data
    global gamestate
    data = {}
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
    await ctx.send("A complete erasure of all data has been done.")
    dump()


#all
@bot.command()
async def ping(ctx):
    '''Returns pong'''
    print("Pong!")
    await ctx.send("Pong!")
    dump()


    
@bot.command(aliases=["notif"])
async def notifyme(ctx):
    '''Use this to get or remove the notify role from yourself'''
    guildd=bot.get_guild(706761016041537539)
    role = discord.utils.get(guildd.roles, name="notify")
    if role in ctx.author.roles:
        await ctx.author.remove_roles(role)
        await ctx.send("You will now not be notified when future games occur.")
    else:
        await ctx.author.add_roles(role)
        await ctx.send("You will now be notified when future games occur.")

@bot.command()
async def notify(ctx):
    '''Use this to ping people who might be willing to play'''
    global lastping
    if lastping==None or datetime.datetime.now()-lastping>timedelta(minutes=30):
        lastping=datetime.datetime.now()
        await ctx.send("<@&706855589883674744> , A game might start soon. Type !signup if you'd like to play.")
    else:
        await ctx.send("Please wait {} longer. The last ping was on {}.".format(timedelta(minutes=30)-(datetime.datetime.now()-lastping),lastping))
    dump()
    
    
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
            starttime=datetime.datetime.now()
            timeoutloop.start()
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

        

@bot.command(aliases=["slist"])
async def signeduplist(ctx):
    msg = await ctx.send("Loading.")
    temp=""
    a=0
    for person in data['signedup']:
        temp+="<@{}> \n".format(person)
        a+=1
    temp+="The number of people who have signed up is- {}".format(a)
    await msg.edit(content=temp)

@bot.command()
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
        if a>b:
            await lobby.send("A game is starting!")
            gamestate =1
            data['gamestate']=1
            await start()
    else:
        await ctx.send("You are currently not playing. Type !signup to join the game.")
    dump()

async def start():
    global data
    global gamestate
    global dekk
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
    elif playernum==6:
        libn=4
        facn=1
    elif playernum==7:
        libn=4
        facn=2
    elif playernum==8:
        libn=5
        facn=2
    elif playernum==9:
        libn=5
        facn=3
    elif playernum==10:
        libn=6
        facn=3
    listoplayers=[]
    rolelist=[]
    for a in range(libn):
        roles.append("Liberal")
    for a in range(facn):
        roles.append("Facist")
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
        data['players'][user]['state']=1
        if data['players'][user]['role']=="Hitler":
            userr=discord.utils.get(guildd.members,id=int(user))
            hitler=userr.name
        elif data['players'][user]['role']=="Facist":
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
        elif data['players'][ath]['role']=="Facist":
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
    print(players)
    data['dekk']=['Liberal Policy','Liberal Policy','Liberal Policy','Liberal Policy','Liberal Policy','Liberal Policy','Facist Policy','Facist Policy','Facist Policy','Facist Policy','Facist Policy','Facist Policy','Facist Policy','Facist Policy','Facist Policy','Facist Policy','Facist Policy']
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
    global prez
    guildd=bot.get_guild(706761016041537539)
    gamestate =2
    data['gamestate']=2
    roundno=data['roundno']
    if len(data['deck'])<3:
        await drawdekk()
    try:
        ath=data['playerorder'][roundno]
        prez=discord.utils.get(guildd.members,id=int(ath))
        guildd=bot.get_guild(706761016041537539)
        data['power']['prez']=data['playerorder'][roundno]
    except:
        data['roundno']=0
        roundno=0
        ath=data['playerorder'][roundno]
        prez=discord.utils.get(guildd.members,id=int(ath))
        guildd=bot.get_guild(706761016041537539)
        data['power']['prez']=data['playerorder'][roundno]
    await lobby.send("Your president is {}. Please nominate a person using !nominate.".format(prez))
    dump()

@bot.command(aliases=["nom"])
@commands.has_role("Players")
async def nominate(ctx,user:discord.Member):
    '''Use this to nominate someone to become chancellor <President>'''
    global data
    global gamestate
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
    msg = await lobby.send("The president has nominated {}! Please react to this message to cast your votes. You have 20 seconds.".format(user.mention))
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
    print(ja,nein)
    dump()
    if ja>nein:
        await lobby.send("{} has been elected as your cancellor!".format(user.name))
        data['power']['chan']=str(user.id)
        if data['faclaw']>2 and data['players'][str(user.id)]['role']=="Hitler":
            await lobby.send("The game is now over! Hitler has become the cancellor!")
            await end("f")
            dump()
            return
        await legis()
    else:
        await fail()
    dump()
    

async def legis():
    global gamestate
    global data
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
    msg = await userr.send("The next three cards in order are {} , {} and {}. React with A , B or C to get rid of the corresponding card. You have 20 seconds to choose.".format(first,second,third))
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
    user=data['power']['chan']
    userr=discord.utils.get(guildd.members,id=int(user))
    msg = await userr.send("The next three cards in order are {} , {} and {}. React with A , B or C to get rid of the corresponding card. You have 20 seconds to choose. Do not select a discarded card.".format(first,second,third))
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
        await user.send("Alright.")
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
                await fail()
                return
            else:
                await lobby.send("The chancellor wanted to veto this agenda but the president didn't agree.")
        else:
            await lobby.send("The chancellor did not want to veto this agenda.")
    await userr.send("Alright you are passing a {}.".format(keep))        
    await picked()
    dump()

async def picked():
    global gamestate
    global data
    global cankill
    guildd=bot.get_guild(706761016041537539)
    role = discord.utils.get(guildd.roles, name="Players")
    chnl=discord.utils.get(guildd.channels,name="lobby")
    await chnl.set_permissions(role,read_messages=True,send_messages=True)
    gamestate =5
    data['gamestate']=5
    await winchecks()
    if cankill==1:
        await lobby.send("The game will continue when the president kills someone.")
        while cankill==1:
            await asyncio.sleep(5)
    await lobby.send("You have 20 seconds to discuss before the next round starts.")
    data['roundno']+=1
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
    cankill=0
    await lobby.send("The president has chosen {} to die.".format(user.mention))
    data['players'][str(user.id)]['state']=0
    data['playerorder'].remove(str(user.id))
    role = discord.utils.get(guildd.roles, name="Players")
    await user.remove_roles(role)
    role = discord.utils.get(guildd.roles, name="Dead")
    await user.add_roles(role)
    if data['players'][str(user.id)]['role']=="Hitler":
        gamestate =6
        data['gamestate']=6
        await lobby.send("Congrats! The liberals have won! They have eliminated hitler!")
        await end("l")
        return
        dump()
    else:
        await lobby.send("That person was not the secret hitler.")
    dump()
        

async def fail():
    global data
    await lobby.send("The government has failed!")
    data['failcounter']+=1
    await board()
    if data['failcounter']>2:
        await lobby.send("The government has failed thrice.")
        nexkt=data['deck'][0]
        data['deck'].pop(0)
        if nexkt=="Liberal Policy":
            data['dekk'].remove('Liberal Policy')
        elif nexkt=="Facist Policy":
            data['dekk'].remove('Facist Policy')
        data['card']=nexkt
        data['failcounter']=0
        await winchecks()
    await lobby.send("You have 20 seconds to discuss before the next round starts.")
    data['roundno']+=1
    await asyncio.sleep(20)
    await lobby.send("Time for next round!")
    await round()
    dump()
    
async def winchecks():
    global gamestate
    global data
    global cankill
    cankill=0
    guildd=bot.get_guild(706761016041537539)
    if data['card']=="Liberal Policy":
        await lobby.send("A liberal law was passed!")
        data['dekk'].remove('Liberal Policy')
        data['liblaw']+=1
        if data['liblaw']>4:
            gamestate =6
            data['gamestate']=6
            await lobby.send("Congrats! The liberals have won!")
            await end("l")
            return
            dump()
    elif data['card']=="Facist Policy":
        await lobby.send("A facist law was passed!")
        data['dekk'].remove('Facist Policy')
        data['faclaw']+=1
        if data['faclaw']>5:
            gamestate =6
            data['gamestate']=6
            await lobby.send("Congrats! The facists have won!")
            await end("f")
            return
            dump()
        elif data['faclaw']==3:
            await lobby.send("Three facist laws have been passed! The previous president has been shown the next three cards.")
            user=data['power']['prez']
            userr=discord.utils.get(guildd.members,id=int(user))
            if len(data['deck'])<3:
                await drawdekk()
            first = data['deck'][0]
            second = data['deck'][1]
            third = data['deck'][2]
            await userr.send("The next three cards in order are {} , {} and {}. You can do anything you want with this information BUT you are not allowed to copy paste this message.".format(first,second,third))
        elif data['faclaw']==4:
            await lobby.send("Four facist laws have been passed! The previous president has the power to kill someone.")
            user=data['power']['prez']
            userr=discord.utils.get(guildd.members,id=int(user))
            await userr.send("Use !kill to kill a person.")
            cankill=1
        elif data['faclaw']==5:
            await lobby.send("Five facist laws have been passed! The previous president has the power to kill someone. Veto power has been unlocked.")
            user=data['power']['prez']
            userr=discord.utils.get(guildd.members,id=int(user))
            await userr.send("Use !kill to kill a person.")
            cankill=1
    await board()
    dump()
            
async def end(who):
    global data
    global gamestate
    win="The winners are-\n"
    lose="The people who didn't win are-\n"
    if who=="l":
        for ath in data['players']:
            if data['players'][ath]['role']=="Liberal":
                win+="<@{}>\n".format(ath)
            else:
                lose+="<@{}>\n".format(ath)
    elif who=="f":
        for ath in data['players']:
            if data['players'][ath]['role']=="Liberal":
                lose+="<@{}>\n".format(ath)
            else:
                win+="<@{}>\n".format(ath)
    await lobby.send("{} \n\n {}".format(win,lose))
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
    data = {}
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
    await lobby.send("Game has been reset")
    dump()
    
async def drawdekk():
    global data
    print(data['deck'])
    print(data['dekk'])
    data['deck']=[]
    random.shuffle(data['dekk'])
    data['deck']=copy.deepcopy(data['dekk'])
    dump()
    
async def board():
    board=discord.Embed(colour=discord.Colour.gold())
    board.set_author(name="The board currently looks like this!")
    liblawn="Cards- "
    faclawn="Cards- "
    failc="Count - "
    for a in range(data['liblaw']):
        liblawn+=":blue_square:"
    for a in range(data['faclaw']):
        faclawn+=":red_square:"
    for a in range(data['failcounter']):
        failc+=":white_circle:"
    board.add_field(name="Liberal Laws- (5 needed to win)",value=liblawn,inline="false")
    board.add_field(name="Facist laws- (6 needed to win,on 3rd you see the next 3 cards, on 4 you can kill, on 5 you can kill and veto is unlocked. After 3 ,if hitler is elected cancellor , facists win.",value=faclawn,inline="false")
    board.add_field(name="Fail counter- ",value=failc,inline="false")
    await lobby.send(embed=board)


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
        await lobby.send("<@&706782757677826078>, the game has taken too long to start and calcelled. Type !j if you still want to play.")
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

@bot.command()
async def displayboard(ctx):
    '''Use this to display the board'''
    await board()

@bot.command()
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

def dump():
    my_collection = db.main
    my_collection.drop()
    my_collection.insert_one(data)
    '''with open('data.json', 'w+') as f:
        json.dump(data, f)'''

keep_alive.keep_alive()
bot.run(token)
