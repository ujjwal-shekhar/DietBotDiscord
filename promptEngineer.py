import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
"""
List of Helpline numbers (can be changed depending on the environment)
"""
helpline_numbers = """
COVID-19 Helpline: 011-23978046 or 1075
National Emergency Number: 112
Police: 100
Fire: 101
Ambulance: 102
Women’s Helpline: 1091
Women’s Helpline (Domestic Abuse): 181
Senior Citizen Helpline: 1091 or 1291
Road Accident Emergency Service: 1073
Children In Difficult Situation: 1098
Kiran Mental Health Helpline: 18005990019This Government helpline may be called for ‘anxiety, depression, stress, panic attack, post-traumatic stress disorder, adjustment disorder, suicidal thoughts, substance abuse, mental health emergency, and pandemic induced psychological issues’.Apart from this, the Jeevan Aastha Helpline is verified for ‘suicide, depression, career counselling and addiction’. Call them at: 18002333330
"""

"""
Returns the user_data JSON

The function currently has a hardcoded JSON as the user_data. 
This will be replaced by the user_data JSON that will be 
fetched from the database.
"""
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

"""
Returns prompt with user_data JSON added to it.

The function currently uses the temporary hardcoded JSON
as the user_data. This will be replaced by the user_data
JSON that will be fetched from the database.

An important note is that the chat_history is hardcoded as 
of now. This will be replaced by the chat_history that will
be fetched from Discord.

"""
def optimize_prompt(prompt):
    user_data = fetch_user_data(None)
    chat_history = user_data.pop("chat_history")
    chat_history = [(chat["human"], chat["bot"]) for chat in chat_history]

    sanity_checked_prompt = check_red_flag_or_optimize(prompt)
    if sanity_checked_prompt['flag'] == "None" or sanity_checked_prompt['flag'] == "NONE" or sanity_checked_prompt['flag'] == "":
        sanity_checked_prompt['optimized_prompt'] = f"""The client data JSON is : {user_data} and the client has asked : {sanity_checked_prompt['optimized_prompt']}"""
    return sanity_checked_prompt, chat_history

"""
Ask ChatGPT if the client prompt has a red flag. If not, optimize the prompt.

Red flags are any harmful thoughts like suicidal thoughts or low self esteem.
We will ask ChatGPT if the prompt any such thoughts and if it does we will
send the appropriate response to the client with resources to seek help.
If there are no red flags, we will optimize the prompt to make it consume 
less tokens.
"""
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
                You are a mental health professional and you are talking to the client. You have to detect potentially harmful thoughts in the client's prompt.
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
                "help" : gpt_ans.split('\n')[1].split(':')[1].strip() + "\n\n\n**HELPLINE NUMBERS**\n\n" + helpline_numbers
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