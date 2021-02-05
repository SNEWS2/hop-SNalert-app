sudo docker run -p 9092:9092 -dit --rm=true --name=scimma-server --hostname localhost scimma/server:latest --noSecurity
sudo docker run -p 27017:27017 -dit --rm --name mongodb --hostname localhost mongo:latest

echo "## The SCiMMA Server container is loading, please wait..."
sleep 20
echo "## The SCiMMA Server container has loaded. Generating the ${OBSERVATION_TOPIC} and ${ALERT_TOPIC} topics..."

echo "starting up the ${OBSERVATION_TOPIC} topic" | hop publish -f BLOB $OBSERVATION_TOPIC --no-auth
echo "starting up the ${ALERT_TOPIC} topic" | hop publish -f BLOB $ALERT_TOPIC --no-auth

echo "## The ${OBSERVATION_TOPIC} and ${ALERT_TOPIC} topics have been loaded."
