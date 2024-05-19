# Other options to run SkyDock AI Suite

## Using the Pre-built Docker Image:
- Pull the Docker image:
```bash
docker pull skydockai/skydock_ai_suite:latest
```

- Configure Environment Variables: Download the [config.env](/config.env) file and update **OPENAI_KEY** with your OpenAI API key.
  (**Note:** If you use Azure OpenAI instead of OpenAI, please see [this instruction](instruction_for_azure_openai.md))

- Run the Docker image:
```bash
docker run --env-file ./config.env -p 8000:8000 skydockai/skydock_ai_suite:latest
```

## Using Docker Compose:
- Clone the source code:
```bash
git clone https://github.com/skydockAI/skydock_ai_suite.git
```

- Configure environment variables: Update the `config.env` or `config_azure.env` file as described above.

- Run with Docker Compose: 
```bash
docker compose up
```
