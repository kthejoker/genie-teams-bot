
webapp_name="${BOT_PREFIX}-geniebot-001"

cd simple-host-bot
mkdir -p bin
source hostbot/bin/activate
pip install -r requirements.txt
pip freeze > requirements.txt
zip -q -r bin/hostbot.zip * -x "hostbot/*" "deploymentTemplates/*" "bin/*"
az webapp deploy --resource-group $RESOURCEGROUPNAME --name ${webapp_name} --src-path bin/hostbot.zip 