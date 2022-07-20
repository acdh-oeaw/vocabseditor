#/bin/bash

docker build -t vocabseditor:latest .
docker run -it -p 8020:8020 --rm --name vocabseditor --env-file .env vocabseditor