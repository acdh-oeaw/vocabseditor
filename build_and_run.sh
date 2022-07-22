#/bin/bash
clear
docker build -t vocabseditor:latest .
echo "##################"
echo "##################"
docker run -it -p 8020:8020 --rm --name vocabseditor --env-file .env_secret vocabseditor