#!/bin/bash
if [[ -z "${RESOURCEGROUPNAME}" ]]; then
    echo "Resource group:"
    read RESOURCEGROUPNAME
fi

webapp_name="${BOT_PREFIX}-genie-skill-001"

cd genie-skill-bot
mkdir -p bin
source geniebot/bin/activate
pip install -r requirements.txt
pip3 freeze > requirements.txt
zip -q -r bin/genieskill.zip * -x "geniebot/*" "deploymentTemplates/*" "bin/*"
az webapp deploy --resource-group $RESOURCEGROUPNAME --name $webapp_name --src-path bin/genieskill.zip 