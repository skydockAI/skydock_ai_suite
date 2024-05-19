#!/bin/bash

if [ "$SLACK_BOT_ENABLED" = "True" ]; then
    echo "RUN AS SLACK BOT"
    python slack_bot.py
else
    echo "RUN AS WEB APP"
    chainlit run -h --host 0.0.0.0 --port "$CHAINLIT_PORT" chainlit_app.py
fi