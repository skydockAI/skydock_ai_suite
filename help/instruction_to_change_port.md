# Instruction to change port
By default, SkyDock AI Suite run on port 8000. If you want to use a different port:
- Open the configuration file and change the variable **CHAINLIT_PORT** from 8000 to the new port that you want to use. This should be done BEFORE running **docker build**
- Run **docker run** with the new port
- In case you use **docker compose**: Update the *ports* section in [compose.yaml](/compose.yaml) file

