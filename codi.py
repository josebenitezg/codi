import asyncio
from dotenv import load_dotenv

from slack_bolt import App
from slack_sdk import WebClient
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Only needed for local development
# load_dotenv()

from utils import (
    SLACK_APP_TOKEN, 
    SLACK_BOT_TOKEN,
    WAIT_MESSAGE,
    update_chat,
    process_conversation_history,
    codeinterpreter
    )

app = App(token=SLACK_BOT_TOKEN)
bot_user_id = app.client.auth_test()["user_id"]
client = WebClient(token=SLACK_BOT_TOKEN)

def get_conversation_history(channel_id, thread_ts):
    return app.client.conversations_replies(
        channel=channel_id,
        ts=thread_ts,
        inclusive=True
    )

@app.event("app_mention")
def command_handler(body, context):
    try:
        channel_id = body['event']['channel']
        thread_ts = body['event'].get('thread_ts', body['event']['ts'])
        bot_user_id = context['bot_user_id']
        slack_resp = app.client.chat_postMessage(
            channel=channel_id,
            thread_ts=thread_ts,
            text=WAIT_MESSAGE
        )
        
        reply_message_ts = slack_resp['message']['ts']
        conversation_history = get_conversation_history(channel_id, thread_ts)
        
        slack_messages, slack_files = process_conversation_history(conversation_history, bot_user_id)

        # Process messages and files form slack to run codeinterpreter
        response = asyncio.run(codeinterpreter(slack_messages, slack_files))
        
        update_chat(app, channel_id, reply_message_ts, response.content)
        
        # Upload images or files
        for file in response.files:
            client.files_upload_v2(
            channels=channel_id,
            thread_ts=thread_ts,
            file=f'{file}'
            )
        
    except Exception as e:
        print(f"Error: {e}")
        app.client.chat_postMessage(
            channel=channel_id,
            thread_ts=thread_ts,
            text=f"I can't provide a response. Encountered an error:\n`\n{e}\n`")

if __name__ == "__main__":
  handler = SocketModeHandler(app, SLACK_APP_TOKEN)
  handler.start()