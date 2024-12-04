# Genie Bot

This project has all of the components required for creating and deploying a Microsoft Teams app that can talk to Databricks Genie. The overall set up is:

* Configure two Azure Bots using the Bot Framework. One acts as an overall host and is surfaced in Teams, and the other is a "Skill" bot that communicates with Databricks Genie.
* Publish these Bots and their dependent resources to Azure.
* Build and deploy a Teams app connected to the  deployed host Azure Bots.

## Prerequisites

- [Python SDK](https://www.python.org/downloads/) min version 3.9
- [Bot Framework Emulator](https://github.com/microsoft/botframework-emulator)
- A Microsoft Azure tenant and privileges to deploy resources there.
- A Microsoft Teams organization and privileges to deploy custom apps there.
- An existing Databricks Genie Space you wish the bot to talk to, in the same Azure tenant.
- [Teams Toolkit CLIv3](https://learn.microsoft.com/en-us/microsoftteams/platform/toolkit/teams-toolkit-cli?pivots=version-three)
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)

Additionally, all instructions assume you are developing, testing, and deploying with Visual Studio Code.

## Part 0. Clone repository and install and configure CLIs

1. Open VS Code, Git: Clone, choose repo.
2. Run az login to connect to the Azure subscription you will deploy resources to.
3. Run ```teamsapp auth login``` to login into your Teams account.
3. Decide on the following pieces of information required to name and deploy resources:
* Azure resource group name and region
* A region to deploy your Azure App Service plan to (typically same as resource group) (eg "East US", "South Central US")
* A short memorable alphanumeric prefix for all Azure Bot resources

## Part 1. Configure environment and bot applications

1. Set following environment variables:

* export RESOURCEGROUPNAME=<your resource group name>
* export LOCATION=<your resource group location> (eg "westus")
* export BOT_PREFIX=<your custom prefix>
* export APP_PLAN_LOCATION=<your App Service Plan location> (eg "westus")
* export DATABRICKS_HOST=<your Azure Databricks workspace URI> (eg https://adb-984752964297111.11.azuredatabricks.net/)
* export DATABRICKS_SPACE_ID=<your Genie Space ID> (from your Genie Space's URL eg 01ef3055390e110b9bb70cca1c8c7a31)
* export DATABRICKS_TOKEN=<a Personal Access Token that has Can Use permissions on the Genie space> (SSO instructions coming soon)

## Part 2. Test Everything Locally
3. Open new terminal, rename HostBot, Run ```source hostbot.sh local```
4. Open new terminal, rename SkilBot, Run ```source skillbot.sh```
4. Open Bot Emulator Framework, connect to local host bot (http://localhost:3978/ap/messages), test with following commands:
* "hello" (Expected response: "Your wish is my command! Say “genie” and your question I’ll patch you through")
* "genie tell me about the data set" (Expected response: Genie explains the dataset)
* Shut down both local bots.

## Deploy Azure Resources and Bot Code

* run ```sh az-create.sh``` to create resource group and Azure Bot, Azure App, and Entra app registration resources for hosting the 2 bots
* run ```sh deploy-genie-skill-code.sh```
* run ```sh deploy-host-bot-code.sh```
* In Azure Portal, navigate to deployed resource group, find Azure Bot for your root bot, go to Test in Web Chat, and test same commands as above.
* Then go to Channels tab and next to Microsoft Teams click on "Open in Teams" to test the bot directly in Teams.

## Deploy Teams App

* Run command ```az bot show -n ${BOT_PREFIX}-geniebot-001 -g ${BOT_PREFIX}-genie-bot --query "properties.msaAppId" -o tsv``` and note the application Id for the root bot.
* Open genie-teams-app/manifest.json.
* Replace bots/botId and webApplicationInfo/id with application ID of Root bot.
* Run command ```sh deploy-genie-teams-app.sh``` to directly install bot as app to Teams.
* Navigate to Teams and begin chatting with installed app (default name "Genie Bot Example")
