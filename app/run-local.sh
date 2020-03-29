# HACK: point to dev environment URLs
echo "Using http://localhost:5000..."
cat app/static/main.mjs | sed s/"https:\/\/muze-player\.herokuapp\.com"/"http:\/\/localhost:5000"/ > temp_main.js
mv temp_main.js app/static/main.mjs

echo "Getting fresh bearer token"
# TODO: use curl to get bearer token?
#cat app/static/player.mjs | sed s/"getBearerTokenFromUrl\(\),"/"grrrrrrrrr"/ > temp_player.js
#mv temp_player.js app/static/player.mjs

# lil trick to open browser after server is started (next cmd)
sleep 1 && open "http://localhost:5000" &
python app/server.py

echo "Resetting environment.."
# TODO: remove bearer token
#cat app/static/player.mjs | sed s/"grrrrrrrrr"/"getBearerTokenFromUrl\(\),"/ > temp_player.js
#mv temp_player.js app/static/player.mjs
cat app/static/main.mjs | sed s/"http:\/\/localhost:5000"/"https:\/\/muze-player\.herokuapp\.com"/ > temp_main.js
mv temp_main.js app/static/main.mjs