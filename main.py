import os
import discord
from discord.ext import tasks
from dotenv import load_dotenv
import vectorDBmaker as llc
import documentQuery as dq

'''
We will import the dotenv module and load the .env file
using the load_dotenv() method. This will load the .env
file and make the environment variables available to us.

This is done to keep the sensitive information like the
TOKEN hidden from the public. We can also use the .env
file to store the database credentials and other sensitive
information.
'''
load_dotenv() # load all the variables from the env file
bot = discord.Bot() # Initialize the bot

"""
Print in the console on load when bot is ready.

We will also initialize the vectorDB here. This 
will be done by using the llmChain functions.

This is an optimization done in order to reduce 
the time taken to query the bot. This is done by 
loading the vectorDB once when the bot is ready
and then using the LLMChain to query the bot.
"""
@bot.event
async def on_ready():
    print(f"""{bot.user} is ready and online!\n\n
              Loading the vectorDB...""")
    
    # Initialize the vectorDB
    global VECTOR_DB
    VECTOR_DB = llc.doc_to_vectordb(llc.load_data_at_url())
                
    print(f"Done loading the vectorDB !\n\n")

"""
Send a direct message to the user when they join the server.

This is done using the `on_member_join` event. We use the
`send` method to send a direct message to the user.
"""
@bot.event
async def on_member_join(member):
    await member.send(f"Hello {member.name}, welcome to the server! How may I help you today?")

"""
Sample `\hello` command to check if the bot is working or not.

Meet the team :) 
- [Ujjwal Shekhar](https://www.linkedin.com/in/ujjwal-shekhar-iiith/)
- [Anika Roy](https://www.linkedin.com/in/anika-roy-210379223/)
- [Himani Belsare](https://www.linkedin.com/in/himani-belsare-8157541bb/)
- [Shashwat Dash](https://www.linkedin.com/in/shashwat-dash-024b37225/)
"""
@bot.slash_command(name = "hello", description = "Say hello to the bot")
async def hello(ctx):
    message="""
    Hello! I am a bot made by Team Diet App:))\n\nHope I can help you with health goals!!
    """
    await ctx.respond(f"{message}")

"""
Send engineered prompt to ChatGPT to receive answers for the user

To do this we use the `UnstructuredURLLoader` URLLoader provided
by LangChain. The URLs that we have used were taken from the 
[ClearCals Blogs Section](https://clearcals.com/blogs). Following
this we use the `doc_to_vectordb` function to convert the document
into a vector database. This is done using the `Chroma` vector store
provided by LangChain. We then use the `vectordb_to_llmChain` function
to convert the vector database into a language model chain. This is
done using the `ChatVectorDBChain` provided by LangChain. We then use
the `query_parser` function to query the language model chain and
receive the answer from the bot. 
"""
@bot.slash_command(name = "askgpt", description = "Query ChatGPT")
async def askGPT(ctx, *, message):
    prompt = f"{message}"
    await ctx.defer()
    response = dq.query_parser(prompt, VECTOR_DB)
    response_to_user = str(response)
    await ctx.followup.send(f"{response_to_user}")

"""
`\dm` command to dm the author
"""
@bot.slash_command(name = "dm", description = "Direct Message the user")
async def direct_message(ctx):
    user = ctx.author
    await ctx.delete()
    await user.send(f"Hello {user.name} I have been summoned! How may I help you today?")

bot.run(os.getenv('TOKEN')) # run the bot with the token
