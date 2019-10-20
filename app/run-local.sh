# Run app locally.

export GOOGLE_APPLICATIONS_CREDENTIALS=$MUZE_PATH_TO_CREDS
export DIALOGFLOW_PROJECT_ID=$MUZE_PROJECT_ID

# run in background
echo "Opening ssh tunnel for port forwarding at muze.serveo.net"
ssh -N -R muze:80:localhost:5000 serveo.net >/dev/null 2>&1 &
SSH_PID=$!

# HACK: point to dev environment URLs
echo "Configuring for local testing..."
cat app/static/modules/player.mjs | sed s/"https:\/\/muze-player\.herokuapp\.com"/"https:\/\/muze.serveo.net"/ > temp_player.js
mv temp_player.js app/static/modules/player.mjs
cat app/static/modules/index.mjs | sed s/"https:\/\/muze-player\.herokuapp\.com"/"http:\/\/localhost:5000"/ > temp_index.js
mv temp_index.js app/static/modules/index.mjs

# lil trick to open browser after server is started (next cmd)
sleep 1 && open "http://localhost:5000" &
python app/server.py

# close tunnel after server is closed
echo "Closing ssh tunnel.."
kill $SSH_PID

cat app/static/modules/player.mjs | sed s/"https:\/\/muze.serveo.net"/"https:\/\/muze-player\.herokuapp\.com"/ > temp_player.js
mv temp_player.js app/static/modules/player.mjs
cat app/static/modules/index.mjs | sed s/"http:\/\/localhost:5000"/"https:\/\/muze-player\.herokuapp\.com"/ > temp_index.js
mv temp_index.js app/static/modules/index.mjs