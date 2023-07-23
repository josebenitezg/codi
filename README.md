# Slack GPT Bot
This repository contains a Python-based Slack GPT Bot that runs [Code Interpreter API](https://github.com/shroominic/codeinterpreter-api)

## Features (Same as CodeInterpreterAPI)
- Dataset Analysis, Stock Charting, Image Manipulation, ....
- Internet access and auto Python package installation
- Input text + files -> Receive text + files
- Conversation Memory: respond based on previous inputs 

## Dependencies
- Python 3.6 or later
- beautifulsoup4
- slack-bolt
- slack-sdk
- codeinterpreterapi
- requests

See `requirements.txt`.

## Installation
1. Clone this repository:

```bash
git clone https://github.com/josebenitezg/codi
cd slack-gpt-bot
```
2. Install the required packages:

```bash
pip install -r requirements.txt
```
3. Create a .env file in the root directory of the project and add your Slack and OpenAI API keys:

```bash
SLACK_BOT_TOKEN=your_slack_bot_token
SLACK_APP_TOKEN=your_slack_app_token
OPENAI_API_KEY=your_openai_api_key
```
See below how to get those.


## Configuring Permissions in Slack
Before you can run the Slack GPT Bot, you need to configure the appropriate permissions for your Slack bot. Follow these steps to set up the necessary permissions:

1. Create [Slack App](https://api.slack.com/authentication/basics)
2. Go to your [Slack API Dashboard](https://api.slack.com/apps) and click on the app you created for this bot.
3. In the left sidebar, click on "OAuth & Permissions".
4. In the "Scopes" section, you will find two types of scopes: "Bot Token Scopes" and "User Token Scopes". Add the following scopes under "Bot Token Scopes":
   - `app_mentions:read`: Allows the bot to read mention events.
   - `chat:write`: Allows the bot to send messages.
5. Scroll up to the "OAuth Tokens for Your Workspace" and click "Install App To Workspace" button. This will generate the `SLACK_BOT_TOKEN`.
6. In the left sidebar, click on "Socket Mode" and enable it. You'll be prompted to "Generate an app-level token to enable Socket Mode". Generate a token named `SLACK_APP_TOKEN` and add the `connections:write` scope.
7. In the "Features affected" section of "Socket Mode" page, click "Event Subscriptions" and toggle "Enable Events" to "On". Add `app_mention` event with the `app_mentions:read` scope in the "Subscribe to bot events" section below the toggle.

## Usage
1. Start the bot:

```
python panchingpt.py
```
2. Invite the bot to your desired Slack channel.
3. Mention the bot in a message and ask a question (including any URLs). The bot will respond with an answer, taking into account any extracted content from URLs.
