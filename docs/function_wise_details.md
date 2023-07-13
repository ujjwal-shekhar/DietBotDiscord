# main.py

## `importing modules and loading files`

> We will import the dotenv module and load the .env file
using the load_dotenv() method. This will load the .env
file and make the environment variables available to us.

>This is done to keep the sensitive information like the
TOKEN hidden from the public. We can also use the .env
file to store the database credentials and other sensitive
information.

```py
import os
import discord
from discord.ext import tasks
from dotenv import load_dotenv
import vectorDBmaker as llc
import documentQuery as dq
```
```py
load_dotenv() # load all the variables from the env file
bot = discord.Bot() # Initialize the bot
```

</br>

##  `on_ready`
### Print in the console on load when bot is ready.

> We will also initialize the vectorDB here. This 
will be done by using the llmChain functions.

> This is an optimization done in order to reduce 
the time taken to query the bot. This is done by 
loading the vectorDB once when the bot is ready
and then using the LLMChain to query the bot.

```py
async def on_ready():
    print(f"""{bot.user} is ready and online!\n\n
              Loading the vectorDB...""")
    
    # Initialize the vectorDB
    global VECTOR_DB
    VECTOR_DB = llc.doc_to_vectordb(llc.load_data_at_url())
                
    print(f"Done loading the vectorDB !\n\n")
```

</br>

## `on_member_join`
 
### Send a direct message to the user when they join the server.

> This is done using the `on_member_join` event. We use the `send` method to send a direct message to the user.

```py
@bot.event
async def on_member_join(member):
    await member.send(f"Hello {member.name}, welcome to the server! How may I help you today?")
```

</br>

## `hello`
### Sample `\hello` command to check if the bot is working or not.

> The bot was made by a team of four members as a part of their
Design and Analysis of Software Systems project assigned to us
by [Susheel Athmakuri](https://www.linkedin.com/in/athmakuri/) 
and [Dr. Sonali Khanra](https://www.linkedin.com/in/dr-sonali-khanra/)
under the guidance of our TA mentor 
[Abhijeeth Singham](https://www.linkedin.com/in/abhijeeth-singam/)
and our professor [Ramesh Loganathan](https://www.linkedin.com/in/rameshl/).
Meet the team :) 
- [Anika Roy](https://www.linkedin.com/in/anika-roy-210379223/)
- [Himani Belsare](https://www.linkedin.com/in/himani-belsare-8157541bb/)
- [Shashwat Dash](https://www.linkedin.com/in/shashwat-dash-024b37225/)
- [Ujjwal Shekhar](https://www.linkedin.com/in/ujjwal-shekhar-iiith/)

``` py
@bot.slash_command(name = "hello", description = "Say hello to the bot")
async def hello(ctx):
    message="""
    Hello! I am a bot made by Team Diet App:))\n\nHope I can help you with health goals!!
    """
    await ctx.respond(f"{message}")
```

</br>

## `askGPT`
### Send engineered prompt to ChatGPT to receive answers for the user

> To do this we use the `UnstructuredURLLoader` URLLoader provided
by LangChain. The URLs that we have used were taken from the 
[ClearCals Blogs Section](https://clearcals.com/blogs). Following
this we use the `doc_to_vectordb` function to convert the document
into a vector database. This is done using the `Chroma` vector store
provided by LangChain. We then use the `vectordb_to_llmChain` function
to convert the vector database into a language model chain. This is
done using the `ChatVectorDBChain` provided by LangChain. We then use
the `query_parser` function to query the language model chain and
receive the answer from the bot. 

```py
@bot.slash_command(name = "askgpt", description = "Query ChatGPT")
async def askGPT(ctx, *, message):
    prompt = f"{message}"
    await ctx.defer()
    response = dq.query_parser(prompt, VECTOR_DB)
    response_to_user = str(response)
    await ctx.followup.send(f"{response_to_user}")
```

</br>

## `direct_message`
### `\dm` command to dm the author

```py
@bot.slash_command(name = "dm", description = "Direct Message the user")
async def direct_message(ctx):
    user = ctx.author
    await ctx.delete()
    await user.send(f"Hello {user.name} I have been summoned! How may I help you today?")

bot.run(os.getenv('TOKEN')) # run the bot with the token
```
</br>

# documentQuery.py
## `vectordb_to_llmChain`

### Convert the vector database into a language model chain.

> We use the `ChatVectorDBChain` provided by LangChain to convert
> the vector database into a language model chain. We use the `OpenAI`
> provided by LangChain to create the language model. The `temperature`
> is used to control the randomness of the model. The `model_name` is
> used to select the model to use. The `return_source_documents` is used
> to return the source documents.

The function returns the language model chain.

```py
def vectordb_to_llmChain(vectordb):
    return ChatVectorDBChain.from_llm(OpenAI(
        temperature=0.2,
        model_name="gpt-3.5-turbo"
    ), vectordb, return_source_documents=True)
```
</br>

## `query_parser`

### Takes the query from the client and returns the answer.

> The function takes the query from the client and returns the answer
> using the `query_parser` function. The `client_prompt` is the query
> from the client. The `chat_history` is the history of the conversation
> between the client and the server.

The function returns the answer.

```py
def query_parser(client_prompt, vectordb):
    qa = vectordb_to_llmChain(vectordb)
    sanitized_prompt, chat_history = prompt_engg.optimize_prompt(client_prompt)

    if sanitized_prompt['flag'] != "None" and sanitized_prompt['flag'] != "NONE" and sanitized_prompt['flag'] != "":
        return sanitized_prompt['help']

    result = qa({
        "question" : sanitized_prompt['optimized_prompt'],
        "chat_history" : chat_history
    })
    source_documents = get_source_documents(result)
    final_answer = format_answer(result["answer"], list(set(source_documents)))
    return final_answer
```

<br>

## `get_source_documents`
### Get source documents from the result obtained.

> The function takes the result obtained from the `query_parser` 
function and returns the list of source documents. The source
documents links are present in the `metadata` of the result's
`source_documents`. 

```py
def get_source_documents(result):
    return [
        result["source_documents"][i].metadata['source']
        for i in range(int(len(result["source_documents"])))
    ]
```

<br>

## `format_answer`
### Return formatted answer to the client.

```py
def format_answer(answer, source_documents):
    final_answer = str(answer) + "\n\n The source documents used were: \n"
    for doc in source_documents:
        final_answer += "\t- "
        final_answer += str(doc)
        final_answer += "\n"
    return final_answer
```

</br>

# promptEngineer.py

## `fetch_user_data`
### Returns the user_data JSON

> The function currently has a hardcoded JSON as the user_data. 
This will be replaced by the user_data JSON that will be 
fetched from the database.

```py
def fetch_user_data(user_id):
    return {
        "general information": {
            "name": "John Doe",
            "age": 25,
            "height": 5.8,
            "weight": 72,
            "sex": "Male"
        },
        "motivation": "I want to lose weight",
        "reason": "I want to look good",
        "goal": "I want to lose 10 pounds",
        "lifestyle": {
            "workout": "I workout 3 times a week",
            "diet": "I eat healthy",
            "sleep": "I sleep 8 hours a day",
            "pace": "very busy",
            "daily working hours": 10
        },
        "mental health":{
            "stress": "I am stressed",
            "disorders": "I have no disorders"
        },
        "amenities available":["gym","park","community classes","trainers","aerobics","stadium"],
        "chat_history":[{
            "human": "Hi! Who should do intermittent fasting?",
            "bot":"Intermittent fasting is not for everyone. People who are underweight or have a history of eating disorders should not fast without consulting with a health professional first. Women should be careful with intermittent fasting and follow separate guidelines, like easing into the practice and stopping immediately if they have any problems like amenorrhea (absence of menstruation). People with certain medical conditions should also consult with a doctor before trying intermittent fasting."
        }]
    }
```

</br>

## `optimize_prompt`
### Returns prompt with user_data JSON added to it.

> The function currently uses the temporary hardcoded JSON
as the user_data. This will be replaced by the user_data
JSON that will be fetched from the database.

> An important note is that the chat_history is hardcoded as 
of now. This will be replaced by the chat_history that will
be fetched from Discord.

```py
def optimize_prompt(prompt):
    user_data = fetch_user_data(None)
    chat_history = user_data.pop("chat_history")
    chat_history = [(chat["human"], chat["bot"]) for chat in chat_history]

    sanity_checked_prompt = check_red_flag_or_optimize(prompt)
    if sanity_checked_prompt['flag'] == "None" or sanity_checked_prompt['flag'] == "NONE" or sanity_checked_prompt['flag'] == "":
        sanity_checked_prompt['optimized_prompt'] = f"""The client data JSON is : {user_data} and the client has asked : {sanity_checked_prompt['optimized_prompt']}"""
    return sanity_checked_prompt, chat_history
```

</br>

## `check_red_flag_or_optimize`
### Ask ChatGPT if the client prompt has a red flag. If not, optimize the prompt.

> Red flags are any harmful thoughts like suicidal thoughts or low self esteem.
We will ask ChatGPT if the prompt any such thoughts and if it does we will
send the appropriate response to the client with resources to seek help.
If there are no red flags, we will optimize the prompt to make it consume 
less tokens.

```py
def check_red_flag_or_optimize(prompt):
    # Modify prompt to get answer from ChatGPT
    user_data = fetch_user_data(None)
    user_data.pop('chat_history')

    flag_prompt = f"""
    Client prompt : "{prompt}"
    """

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role":"system",
                "content":r"""
                You are a mental health professaional and you are talking to the client. You have to detect potentially harmful thoughts in the client's prompt.
                Strictly follow the output format given as :
                flag : <flag_value> --> None, if no negative thoughts
                help : <help_message_for_client> --> None, if no negative thoughts
                """
            },
            {
                "role":"user",
                "content": flag_prompt
            }
        ]
    )

    gpt_ans = completion.choices[0].message.content
    flag_value = gpt_ans.split('\n')[0].split(':')[1].strip()
    try :
        if flag_value != "None" and flag_value != "NONE" and flag_value != "":
            return {
                "flag" : flag_value,
                "help" : gpt_ans.split('\n')[1].split(':')[1].strip()
            }
        else:
            return {
                "flag" : "None",
                "optimized_prompt" : prompt
            }
    except:
        return {
            "flag" : "None",
            "optimized_prompt" : prompt
        }
```

<br>

# vectorDBmaker

## `load_data_at_url`

### Load the data from the URLs provided.

> The URLs that we have used were taken from the 
[ClearCals Blogs Section](https://clearcals.com/blogs).

> We use the LangChain `UnstructuredURLLoader` to load the data using the list of URLs provided. 

> The function returns the data using the `load` method.

```py
def load_data_at_url():
    # Load the document
    urls = os.getenv('CONTEXT_URLS').split(',')
    loader = UnstructuredURLLoader(urls)
    data = loader.load()
    return data
```

</br>

## `doc_to_vectordb`
### Convert the document into a vector database.

> We use the `Chroma` vector store provided by LangChain to convert
the document into a vector database. We use the `OpenAIEmbeddings`
provided by LangChain to create the embedding. The `TokenTextSplitter`
provided by LangChain is used to split the document into chunks.
The `persist_directory` is used to store the vector database.

> The function returns the vector database.

```py
def doc_to_vectordb(document):
    # Persist directory
    if platform.system() == 'Windows':
        persist_dir = os.path.join(os.environ['USERPROFILE'], 'chromadb')
    else:
        persist_dir = os.path.join(os.environ['HOME'], 'chromadb')

    # Create the embedding
    splitter = TokenTextSplitter(chunk_size=1000, chunk_overlap=0)
    split_doc = splitter.split_documents(document)

    embeddings = OpenAIEmbeddings()
    vectordb = Chroma.from_documents(split_doc, embeddings, 
                                     persist_directory=persist_dir)
    vectordb.persist()

    return vectordb
```