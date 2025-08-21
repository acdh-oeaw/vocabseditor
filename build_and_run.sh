#/bin/bash
clear
docker build -t vocabseditor:latest .
echo "##################"
echo "##################"
docker run -it --network="host" --rm --name vocabseditor --env-file .env vocabseditor