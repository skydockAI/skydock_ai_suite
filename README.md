# Welcome to SkyDock AI Suite 👋

**Launch your own AI-powered application suite and enhance team productivity in just minutes! ⚡️**

SkyDock AI Suite is a comprehensive Docker image crafted to help businesses harness the power of the latest AI technologies from OpenAI in a secure manner. Designed for team productivity, this suite includes features like image generation, speech-to-text conversion, and PowerPoint presentation creation. As an evolving project, SkyDock AI Suite will continue to expand its capabilities, adding even more powerful features to help businesses and individuals leverage AI advancements.

- ✅ Conversation History
- ✅ GPT Vision Support
- ✅ Document Attachment Support
- ✅ Image Generation
- ✅ Text to Speech Conversion
- ✅ Speech to Text Conversion
- ✅ Powerpoint Presentation Generation


## 🚀 Quickstart
- Clone the source code:
```bash
git clone https://github.com/skydockAI/skydock_ai_suite.git
```

- Build the Docker image:
```bash
docker build -t skydock_ai_suite:latest .
```
- Configure Environment Variables: Download the [config.env](config.env) file and update the first three variables (**SLACK_SOCKET_TOKEN**, **SLACK_BOT_USER_TOKEN**, and **OPENAI_KEY**) with your Slack app tokens and OpenAI API key.
  (**Note:** If you use Azure OpenAI instead of OpenAI, please see [this instruction](instruction_for_azure_openai.md))

- Run the Docker image:
```bash
docker run --env-file ./config.env skydock_ai_suite:latest
```
**Note:** 
- Other options to run SkyDock AI Suite can be found [here](instruction_to_run.md)
- Read [this instruction](instruction_for_powerpoint_template.md) if you want to use your own PowerPoint template file


## Key Features:
- **Conversation History**: Maintains the context of each conversation within a Slack thread, ensuring continuity and ease of reference.
<img src="/images/conversation_history.png" alt="Conversation History"></img>

- **GPT Vision Support**: Utilizes the gpt-4-turbo model to provide cutting-edge vision capabilities.
<img src="/images/gpt_vision.png" alt="GPT Vision Support"></img>

- **Document Attachment Support**: Allows users to input information via document attachments. Currently supports .txt, .docx, and .pdf file formats.
<img src="/images/document_attachment.png" alt="GPT Vision Support"></img>

- **Image Generation**: Leverages the Dall-E models to support creative and dynamic image generation.
<img src="/images/image_generation.png" alt="Image Generation"></img>

- **Text to Speech Conversion**: Converts text messages into spoken words, enhancing accessibility.
<img src="/images/tts.png" alt="Text to Speech Conversion"></img>

- **Speech to Text Conversion**: Uses the Whisper model to transcribe spoken words into text, facilitating easy communication.
<img src="/images/stt.png" alt="Speech to Text Conversion"></img>

- **Powerpoint Presentation Generation**: Automatically creates PowerPoint presentations on a specified topic or based on input document.
<img src="/images/presentation_generation.png" alt="Speech to Text Conversion"></img>


## License:
**SkyDock AI Suite** is open-source and licensed under the [GPL-3.0](LICENSE) license.
