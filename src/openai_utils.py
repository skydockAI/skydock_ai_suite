from openai import OpenAI, AzureOpenAI, AsyncOpenAI, AsyncAzureOpenAI
import base64
import random
import time
import os
from types import SimpleNamespace

def create_ai_client():
    OPENAI_KEY = os.getenv("OPENAI_KEY")
    AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_VERSION = os.getenv("AZURE_OPENAI_VERSION")

    if OPENAI_KEY:
        print("Running with OpenAI")
        ai_client = OpenAI(api_key=OPENAI_KEY)
    elif AZURE_OPENAI_KEY:
        print("Running with Azure OpenAI")
        ai_client = AzureOpenAI(api_key = AZURE_OPENAI_KEY, api_version=AZURE_OPENAI_VERSION, azure_endpoint=AZURE_OPENAI_ENDPOINT)
    else:
        print("[ERROR] Missing both OPENAI_KEY and AZURE_OPENAI_KEY")
        exit(1)
    return ai_client

def get_gpt_response(ai_client, gpt_model, system_prompt, conversation_history, tools):
    prompt_structure = [{"role": "system", "content": system_prompt}]
    for msg in conversation_history:
        prompt_structure.append(msg) 
    try:
        response = ai_client.chat.completions.create(
            model = gpt_model,
            messages = prompt_structure,
            tools = tools,
            tool_choice = "auto"
        )
        return response.choices[0].message
    except Exception as e:
        return SimpleNamespace(content=f"[ERROR] Problem calling OpenAI API:\n {e}")

def generate_image(ai_client, image_model, input_text, size = "square"):
    if size == "portrait":
        image_size = "1024x1792"
    elif size == "landscape":
        image_size = "1792x1024"
    else:
        image_size = "1024x1024"
    response = ai_client.images.generate(model = image_model, prompt = input_text, size = image_size, quality = "standard", n=1)
    return response.data[0].url

def generate_tts(ai_client, file_folder, tts_model, tts_voice, input_text):
    speech_file_path = f'{file_folder}/{generate_random_file_name()}.mp3'
    with ai_client.audio.speech.with_streaming_response.create(model = tts_model, voice = tts_voice, input = input_text) as response:
        response.stream_to_file(speech_file_path)
    return speech_file_path

def generate_stt(ai_client, file_path, stt_model):
    audio_file= open(file_path, "rb")
    response = ai_client.audio.transcriptions.create(model = stt_model, file = audio_file, response_format="text")
    return response

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def generate_random_file_name():
    return f'{int(time.time_ns())}_{random.randint(0,10000)}'

def get_file_extension(file_path):
    _, file_extension = os.path.splitext(file_path)
    return file_extension

def generate_tools_list():
    IMAGE_GENERATION_ENABLED = os.getenv('IMAGE_GENERATION_ENABLED', 'False').lower() in ('true', '1')
    TEXT_TO_SPEECH_ENABLED = os.getenv('TEXT_TO_SPEECH_ENABLED', 'False').lower() in ('true', '1')
    SPEECH_TO_TEXT_ENABLED = os.getenv('SPEECH_TO_TEXT_ENABLED', 'False').lower() in ('true', '1')
    POWERPOINT_GENERATION_ENABLED = os.getenv('POWERPOINT_GENERATION_ENABLED', 'False').lower() in ('true', '1')
    GRAPH_GENERATION_ENABLED = os.getenv('GRAPH_GENERATION_ENABLED', 'False').lower() in ('true', '1')

    tools = []
    if IMAGE_GENERATION_ENABLED:
        tools.append({
            "type": "function",
            "function": {
                "name": "generate_image",
                "description": "Generate image basing on description",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Description of the image, e.g. a house under an apple tree",
                        },
                        "size": {
                            "type": "string",
                            "enum": ["square", "portrait", "landscape"],
                            "description": "Size of the generated image. Use square if no information is provided",
                        }
                    },
                    "required": ["description"],
                }
            },
        })
        print('IMAGE_GENERATION: Enabled')
    else:
        print('IMAGE_GENERATION: Disabled')

    if TEXT_TO_SPEECH_ENABLED:
        tools.append({
            "type": "function",
            "function": {
                "name": "generate_tts",
                "description": "Generate or convert from text to speech",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input_text": {
                            "type": "string",
                            "description": "Text to be converted to speech",
                        }
                    },
                    "required": ["input_text"],
                }
            },
        })
        print('TEXT_TO_SPEECH: Enabled')
    else:
        print('TEXT_TO_SPEECH: Disabled')

    if SPEECH_TO_TEXT_ENABLED:
        tools.append({
            "type": "function",
            "function": {
                "name": "generate_stt",
                "description": "Transcript or convert from speech to text",
                "parameters": {
                    "type": "object",
                    "properties": {
                    }
                }
            },
        })
        print('SPEECH_TO_TEXT: Enabled')
    else:
        print('SPEECH_TO_TEXT: Disabled')

    if POWERPOINT_GENERATION_ENABLED:
        tools.append({
            "type": "function",
            "function": {
                "name": "generate_presentation",
                "description": "Generate contents for powerpoint presentation slides for a specific topic or basing on provided information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Topic of the presentation",
                        },
                        "slide_data": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {
                                        "type": "string",
                                        "description": "Title of the slide"
                                    },
                                    "content": {
                                        "type": "array",
                                        "items": {
                                            "type": "string",
                                            "description": "Content for one bullet point"
                                        },
                                        "description": "An array of main contents of the slide"
                                    }
                                }
                            },
                            "description": "An array of slide contents",
                        }
                    },
                    "required": ["topic", "slide_data"],
                }
            }
        })
        print('POWERPOINT_GENERATION: Enabled')
    else:
        print('POWERPOINT_GENERATION: Disabled')

    if GRAPH_GENERATION_ENABLED:
        tools.append({
            "type": "function",
            "function": {
                "name": "generate_graph",
                "description": "Generate graph or diagram from DOT language using Graphviz library",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "graph_data": {
                            "type": "string",
                            "description": "Graph data in DOT language format",
                        }
                    },
                    "required": ["graph_data"],
                }
            },
        })
        print('GRAPH_GENERATION_ENABLED: Enabled')
    else:
        print('GRAPH_GENERATION_ENABLED: Disabled')

    return tools