# Run app locally.

export GOOGLE_APPLICATIONS_CREDENTIALS=$MUZE_PATH_TO_CREDS
export DIALOGFLOW_PROJECT_ID=$MUZE_PROJECT_ID

# run in background
echo "Opening ssh tunnel for port forwarding at muze.serveo.net"
ssh -N -R muze:80:localhost:5000 serveo.net >/dev/null 2>&1 &
SSH_PID=$!

# lil trick to open browser after server is started (next cmd)
sleep 1 && open "http://localhost:5000" &
python app/server.py >server_output.txt 2>&1

# close tunnel after server is closed
echo "Closing ssh tunnel.."
kill $SSH_PID
