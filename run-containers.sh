sudo docker run -p 9092:9092 -dit --rm=true --name=scimma-server --hostname localhost scimma/server:latest --noSecurity
sudo docker run -p 27017:27017 -dit --rm --name mongodb --hostname localhost mongo:latest

