from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import requests
import os
import json
import re
from openai_utils import *
from document_utils import *
from powerpoint_generator import create_powerpoint_file
from graph_generator import create_graph_file

SLACK_SOCKET_TOKEN = os.getenv("SLACK_SOCKET_TOKEN")
SLACK_BOT_USER_TOKEN = os.getenv("SLACK_BOT_USER_TOKEN")

WAITING_MESSAGE = os.getenv("WAITING_MESSAGE")
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")
TEMP_FILES_FOLDER = os.getenv("TEMP_FILES_FOLDER")

GPT_MODEL = os.getenv("GPT_MODEL")
TTS_MODEL = os.getenv("TTS_MODEL")
TTS_VOICE = os.getenv("TTS_VOICE")
IMAGE_MODEL = os.getenv("IMAGE_MODEL")
STT_MODEL = os.getenv("STT_MODEL")

app = App(token = SLACK_BOT_USER_TOKEN)
ai_client = create_ai_client()
tools = generate_tools_list()

@app.message()
def im_message(client, message):
    if message["channel_type"] == "im": # Direct message
        reply = client.chat_postMessage(channel = message["channel"], thread_ts = message["ts"], text = WAITING_MESSAGE)
        response = process_conversation(client, message)
        client.chat_update(channel = message["channel"], ts = reply["ts"], text = response)
        
@app.event("app_mention")
def handle_app_mention_events(client, body):
    message = body["event"]
    reply = client.chat_postMessage(channel = message["channel"], thread_ts = message["ts"], text = WAITING_MESSAGE)
    response = process_conversation(client, message)
    client.chat_update(channel = message["channel"], ts = reply["ts"], text = response)

#============================================#
def process_conversation(client, message):
    conversation_history = get_conversation_history(client, message)
    result = get_gpt_response(ai_client, GPT_MODEL, SYSTEM_PROMPT, conversation_history, tools)
    if result.content:
        response = result.content
    elif result.tool_calls:
        function_name = result.tool_calls[0].function.name
        arguments = json.loads(result.tool_calls[0].function.arguments)
        if function_name == "generate_image":
            description = arguments["description"]
            try:
                size = arguments["size"]
            except:
                size = "square"
            try:
                image_url = generate_image(ai_client, IMAGE_MODEL, description, size)
                image_content = requests.get(image_url)
                image_filepath = f'{TEMP_FILES_FOLDER}/{generate_random_file_name()}.jpg'
                with open(image_filepath, "wb") as f:
                    f.write(image_content.content)
                client.files_upload_v2(channel = message["channel"], thread_ts = message["ts"], file = image_filepath, title = description)
                response = f'[SUCCESS] Image has been generated successfully'
                clean_up_file(image_filepath)
            except Exception as e:
                response = f'[ERROR] Problem generating image using DALL-E:\n {e}'
        elif function_name == "generate_tts":
            input_text = arguments["input_text"]
            try:
                generated_file = generate_tts(ai_client, TEMP_FILES_FOLDER, TTS_MODEL, TTS_VOICE, input_text)
                client.files_upload_v2(channel = message["channel"], thread_ts = message["ts"], file = generated_file, title = "Text To Speech")
                response = f'[SUCCESS] Your text has been converted to speech'
                clean_up_file(generated_file)
            except Exception as e:             
                response = f'[ERROR] Problem converting from text to speech:\n {e}'
        elif function_name == "generate_stt":
            if "files" in message:
                try:
                    file_path = save_uploaded_file(message["files"][0])
                    response = f'[SUCCESS] {generate_stt(ai_client, file_path, STT_MODEL)}'
                    clean_up_file(file_path)
                except Exception as e:
                    response = f'[ERROR] Problem converting from speech to text:\n {e}'
            else:
                response = f'[ERROR] No attached audio found in your message'
        elif function_name == "generate_presentation":
            topic = arguments["topic"]
            slide_data = arguments["slide_data"]
            generated_file = create_powerpoint_file(topic, slide_data, TEMP_FILES_FOLDER)
            client.files_upload_v2(channel = message["channel"], thread_ts = message["ts"], file = generated_file, title = "Powerpoint presentation")
            response = f'[SUCCESS] Your Powerpoint presentation has been generated successfully'
            clean_up_file(generated_file)
        elif function_name == "generate_graph":
            graph_data = arguments["graph_data"]
            output_file_name = f'{TEMP_FILES_FOLDER}/{generate_random_file_name()}'
            generated_file = create_graph_file(graph_data, output_file_name)
            client.files_upload_v2(channel = message["channel"], thread_ts = message["ts"], file = generated_file, title = "Graph")
            response = f'[SUCCESS] Your graph has been generated successfully'
            clean_up_file(generated_file)
        else:
            response = f"[ERROR] Invalid function"
    else:
        response = f"[ERROR] Invalid response from OpenAI"
    return response

def get_conversation_history(client, message):
    result = []
    if "thread_ts" in message:
        conversation = client.conversations_replies(channel = message["channel"], ts = message["thread_ts"])
        if "messages" in conversation:
            for msg in conversation["messages"]:
                if "client_msg_id" in msg:
                    gpt_message = create_gpt_user_message_from_slack_message(msg)
                    result.append(gpt_message)
                if "bot_id" in msg:
                    if msg["text"] != WAITING_MESSAGE:
                        result.append({"role": "assistant", "content": msg["text"]})
    else:
        gpt_message = create_gpt_user_message_from_slack_message(message)
        result.append(gpt_message)
    return result

def save_uploaded_file(file):
    url = file["url_private"]
    file_path = f'{TEMP_FILES_FOLDER}/{generate_random_file_name()}.{file["filetype"]}'
    headers = {"Authorization": "Bearer " + SLACK_BOT_USER_TOKEN}
    response = requests.get(url, headers = headers)
    with open(file_path, "wb") as f:
        f.write(response.content)
    return file_path

def create_gpt_user_message_from_slack_message(slack_message):
    if "files" in slack_message:
        attached_file = slack_message["files"][0]
        attached_file_type = attached_file["filetype"].lower()
        if attached_file_type in ["png", "jpg", "jpeg", "gif", "webp"]:
            image_file = save_uploaded_file(attached_file)
            base64_image = encode_image(image_file)
            result = {
                "role": "user",
                "content": [
                    {"type": "text", "text": slack_message["text"]},
                    {
                        "type": "image_url",
                        "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                ],
            }
            clean_up_file(image_file)
        elif attached_file_type in ["txt", "text", "docx", "pdf"]:
            document_file = save_uploaded_file(attached_file)
            file_content = read_all_text_from_file(document_file)
            prompt_content = slack_message["text"] + ":\nHere is the provided information in the attached document:\n" + file_content
            result = {"role": "user", "content": prompt_content}
            clean_up_file(document_file)
        else:
            result = {"role": "user", "content": slack_message["text"]}
    else:
        result = {"role": "user", "content": slack_message["text"]}
    return result

def clean_up_file(file_path):
    try:
        os.remove(file_path)
    except:
        pass

def remove_mentions(text):
    pattern = r'<@.*?>'
    return re.sub(pattern, '', text)

#============================================#

# Create folder for temporary files if not exist
if not os.path.exists(TEMP_FILES_FOLDER):
    os.makedirs(TEMP_FILES_FOLDER)
# Start the bot
if __name__ == "__main__":
    SocketModeHandler(app, SLACK_SOCKET_TOKEN).start()
