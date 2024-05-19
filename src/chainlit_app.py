import chainlit as cl
import os
import json
import requests
from openai_utils import *
from document_utils import *
from powerpoint_generator import create_powerpoint_file
from graph_generator import create_graph_file

TEMP_FILES_FOLDER = ".files"

SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")
GPT_MODEL = os.getenv("GPT_MODEL")
TTS_MODEL = os.getenv("TTS_MODEL")
TTS_VOICE = os.getenv("TTS_VOICE")
IMAGE_MODEL = os.getenv("IMAGE_MODEL")
STT_MODEL = os.getenv("STT_MODEL")

ai_client = create_ai_client()
tools = generate_tools_list()

@cl.on_message
async def main(message: cl.Message):
    # Create folder for temporary files for current user if not exist
    user_temp_file_folder = f'{TEMP_FILES_FOLDER}/{cl.user_session.get("id")}'
    if not os.path.exists(user_temp_file_folder):
        os.makedirs(user_temp_file_folder)
    
    save_message_to_history(message)

    #Create an empty response to show loading icon
    response_msg = cl.Message(content="")
    await response_msg.send()
    
    #Call OpenAI
    conversation_history = get_conversation_history()
    result = await cl.make_async(get_gpt_response)(ai_client, GPT_MODEL, SYSTEM_PROMPT, conversation_history, tools)
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
                image_url = await cl.make_async(generate_image)(ai_client, IMAGE_MODEL, description, size)
                image_content = await cl.make_async(requests.get)(image_url)
                random_file_name = generate_random_file_name()
                image_filepath = f'{TEMP_FILES_FOLDER}/{cl.user_session.get("id")}/{random_file_name}.png'
                with open(image_filepath, "wb") as f:
                    f.write(image_content.content)
                attached_image = cl.Image(path=image_filepath, name=random_file_name, display="inline", size="large")
                response_msg.elements = [attached_image]
                response = f'[SUCCESS] Image has been generated successfully'
            except Exception as e:
                response = f'[ERROR] Problem generating image using DALL-E:\n {e}'
        elif function_name == "generate_tts":
            input_text = arguments["input_text"]
            try:
                generated_file_path = await cl.make_async(generate_tts)(ai_client, f'{TEMP_FILES_FOLDER}/{cl.user_session.get("id")}', TTS_MODEL, TTS_VOICE, input_text)
                attached_audio = cl.Audio(name="Generated Text To Speech", path=generated_file_path, display="inline")
                response_msg.elements = [attached_audio]
                response = f'[SUCCESS] Your text has been converted to speech'
            except Exception as e:             
                response = f'[ERROR] Problem converting from text to speech:\n {e}'
        elif function_name == "generate_stt":
            if message.elements:
                try:
                    attached_files = [file for file in message.elements]
                    output_text = await cl.make_async(generate_stt)(ai_client, attached_files[0].path, STT_MODEL)
                    response = f'[SUCCESS] {output_text}'
                except Exception as e:             
                    response = f'[ERROR] Problem converting from speech to text:\n {e}'
            else:
                response = f'[ERROR] No attached audio found in your message'
        elif function_name == "generate_presentation":
            topic = arguments["topic"]
            slide_data = arguments["slide_data"]
            generated_file_path = await cl.make_async(create_powerpoint_file)(topic, slide_data, f'{TEMP_FILES_FOLDER}/{cl.user_session.get("id")}')
            attached_file = cl.File(name=topic, path=generated_file_path, display="inline")
            response_msg.elements = [attached_file]
            response = f'[SUCCESS] Your Powerpoint presentation has been generated successfully'
        elif function_name == "generate_graph":
            graph_data = arguments["graph_data"]
            output_file_name = f'{TEMP_FILES_FOLDER}/{cl.user_session.get("id")}/{generate_random_file_name()}'
            generated_file_path = await cl.make_async(create_graph_file)(graph_data, output_file_name)
            attached_image = cl.Image(path=generated_file_path, name="Generated Graph", display="inline", size="large")
            response_msg.elements = [attached_image]
            response = f'[SUCCESS] Your graph has been generated successfully'
        else:
            response = f"[ERROR] Invalid function"
    else:
        response = f"[ERROR] Invalid response from OpenAI"
    
    response_msg.content = response
    await response_msg.update()
    save_message_to_history(response_msg)


#============================================#

def save_message_to_history(message):
    if cl.user_session.get("chat_history"):
        chat_history = cl.user_session.get("chat_history")
    else:
        chat_history = []
    chat_history.append(message)
    cl.user_session.set("chat_history", chat_history)

def get_conversation_history():
    result = []
    if cl.user_session.get("chat_history"):
        for message in cl.user_session.get("chat_history"):
            if message.author == "User":
                processed_message = {"role": "user", "content": message.content}
                if message.elements:
                    try:
                        attached_files = [file for file in message.elements]
                        first_file = attached_files[0]
                        file_extension = get_file_extension(first_file.name).lower()
                        if file_extension in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
                            base64_image = encode_image(first_file.path)
                            processed_message = {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": message.content},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                        }
                                    }
                                ]
                            }
                        elif file_extension in [".txt", ".docx", ".pdf"]:
                            file_content = read_all_text_from_file(first_file.path, file_extension)
                            prompt_content = message.content + ":\nHere is the provided information in the attached document:\n" + file_content
                            processed_message = {"role": "user", "content": prompt_content}
                    except Exception as e:             
                        pass
                result.append(processed_message)
            else:
                result.append({"role": "assistant", "content": message.content})
    return result

