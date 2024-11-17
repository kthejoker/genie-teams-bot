
az login
if [[ -z "${LOCATION}" ]]; then
  echo "App Plan Service Location (eg westus):"
  read LOCATION
fi
if [ $(az group exists --name $RESOURCEGROUPNAME) = false ]; then
    az group create --name $RESOURCEGROUPNAME --location $LOCATION --tags Owner=kyle.hale@databricks.com
    #az group create --name $RESOURCEGROUPNAME --location $LOCATION
fi

export MicrosoftAppId="$(az ad app create --display-name "Genie Root Bot" --sign-in-audience "AzureADMultipleOrgs" --query "appId" -o tsv)"
export MicrosoftAppPassword="$(az ad app credential reset --id $MicrosoftAppId --query "password" -o tsv)"

rootBot="${BOT_PREFIX}-geniebot-001"
app_plan="${BOT_PREFIX}-genie-appplan"
appService="${BOT_PREFIX}-genie-skill-001"
az deployment group create --resource-group $RESOURCEGROUPNAME --template-file "simple-host-bot/deploymentTemplates/template-BotApp-with-rg.json" --parameters appServiceName=${rootBot} newAppServicePlanName=${app_plan} appId=${MicrosoftAppId} appSecret=${MicrosoftAppPassword} bot_prefix=${BOT_PREFIX}
az deployment group create --resource-group $RESOURCEGROUPNAME --template-file "simple-host-bot/deploymentTemplates/template-AzureBot-with-rg.json" --parameters  azureBotId=${rootBot} appId=${MicrosoftAppId}
        
if [[ -z "${MicrosoftAppId_Skill}" ]]; then
  export MicrosoftAppId_Skill="$(az ad app create --display-name "Genie Skill Bot" --sign-in-audience "AzureADMultipleOrgs" --query "appId" -o tsv)"
  export MicrosoftAppPassword_Skill="$(az ad app credential reset --id $MicrosoftAppId_Skill | jq '.["password"]' --raw-output)"
fi

az deployment group create --resource-group $RESOURCEGROUPNAME --template-file "genie-skill-bot/deploymentTemplates/template-BotApp-with-rg.json" --parameters appServiceName=${appService} existingAppServicePlanName=${app_plan}  appType='MultiTenant' appId=${MicrosoftAppId_Skill} appSecret=${MicrosoftAppPassword_Skill} tenantId=$MicrosoftAppTenantId databricks_host=${DATABRICKS_HOST} databricks_token=${DATABRICKS_TOKEN} databricks_space_id=${DATABRICKS_SPACE_ID}
az deployment group create --resource-group $RESOURCEGROUPNAME --template-file "genie-skill-bot/deploymentTemplates/template-AzureBot-with-rg.json" --parameters azureBotId=${appService} botEndpoint="" appType="MultiTenant" appId=$MicrosoftAppId_Skill tenantId=$MicrosoftAppTenantId
