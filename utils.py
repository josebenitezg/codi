import os
import re
import asyncio
import logging
import requests

from trafilatura import extract, fetch_url
from trafilatura.settings import use_config

from codeinterpreterapi import CodeInterpreterSession, File

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

WAIT_MESSAGE = "Working on it! 🧪"

newconfig = use_config()
newconfig.set("DEFAULT", "EXTRACTION_TIMEOUT", "0")
logger = logging.getLogger(__name__)
headers = {'Authorization': 'Bearer %s' % SLACK_BOT_TOKEN}

def update_chat(app, channel_id, reply_message_ts, response_text):
    app.client.chat_update(
        channel=channel_id,
        ts=reply_message_ts,
        text=response_text
    )

def process_conversation_history(conversation_history, bot_user_id):
    slack_files = []

    for message in conversation_history['messages'][:-1]:
        if 'files' in message:
            for file in message.get('files', []):
                url = file.get('url_private')
                file_name = file.get('name')
                try:
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()
                except requests.exceptions.HTTPError as err:
                    logger.info(f"Failed to download the file. HTTP Status Code: {response.status_code}, Error: {err}")
                    continue
                except Exception as err:
                    logger.info(f"An error occurred: {err}")
                    continue

                with open(file_name, 'w') as file_obj:
                    file_obj.write(response.text)
                logger.info("File downloaded successfully")
                slack_files.append(file_name)

        message_text = process_message(message, bot_user_id)
        if message_text:
            return message_text, slack_files
    
    return None, slack_files

def process_message(message, bot_user_id):
    message_text = message['text']
    role = "assistant" if message['user'] == bot_user_id or message.get("subtype") == "bot_message" or message.get("bot_id") else "user"
    if role == "user":
        url_list = extract_url_list(message_text)
        if url_list:
            message_text = augment_user_message(message_text, url_list)
    message_text = clean_message_text(message_text, role, bot_user_id)
    return message_text

def clean_message_text(message_text, role, bot_user_id):
    if (f'<@{bot_user_id}>' in message_text) or (role == "assistant"):
        message_text = message_text.replace(f'<@{bot_user_id}>', '').strip()
        return message_text
    return None

def extract_url_list(text):
    url_pattern = re.compile(
        r'<(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)>'
    )
    url_list = url_pattern.findall(text)
    return url_list if len(url_list)>0 else None

def augment_user_message(user_message, url_list):
    all_url_content = ''
    for url in url_list:
        downloaded = fetch_url(url)
        url_content = extract(downloaded, config=newconfig)
        user_message = user_message.replace(f'<{url}>', '')
        all_url_content = all_url_content + f' Contents of {url} : \n """ {url_content} """'
    user_message = user_message + "\n" + all_url_content
    return user_message

async def codeinterpreter(user_input, slack_files):
    # create a session
    session = CodeInterpreterSession()
    await session.astart()
    
    if slack_files is not None:
        slack_files = [File.from_path(file) for file in slack_files]
    print(slack_files)
    # generate a response based on user input
    response =  await session.generate_response(user_input, files=slack_files)
    
    # ouput the response (text + image)
    print("AI: ", response.content)
    
    for file in response.files:
        file.save(f'{file}')
        
    # terminate the session
    await session.astop()
    
    return response


