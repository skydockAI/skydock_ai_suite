# Instruction to run SkyDock AI Suite as a Slack bot
By default, SkyDock AI Suite runs as a web application. Follow these steps if you want to run it as a Slack bot:
- Open the configuration file and set the variable **SLACK_BOT_ENABLED** to True
- Update the 2 variables **SLACK_SOCKET_TOKEN** and **SLACK_BOT_USER_TOKEN** with your Slack tokens
- When running as a Slack bot, you don't need to map port 8000 when running the Docker image:
```bash
docker run --env-file ./config.env skydock_ai_suite:latest
```