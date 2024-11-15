"""
Databricks Genie Bot

Author: Luiz Carrossoni Neto / Kyle Hale
Revision: 1.1

This script implements an experimental chatbot that interacts with Databricks' Genie API,
which is currently in Private Preview. The bot facilitates conversations with Genie,
Databricks' AI assistant, through a chat interface.

Note: This is experimental code and is not intended for production use.
"""

import os

import time
from aiohttp import web
from botbuilder.core import BotFrameworkAdapterSettings, BotFrameworkAdapter, ActivityHandler, TurnContext
from botbuilder.schema import Activity, ChannelAccount
from config import DefaultConfig
from bots.genie_bot import GenieBot

from http import HTTPStatus

from aiohttp import web
from aiohttp.web import Request, Response
from aiohttp.web_response import json_response
from botbuilder.integration.aiohttp import ConfigurationBotFrameworkAuthentication
from botframework.connector.auth import AuthenticationConfiguration

from config import DefaultConfig
from authentication import AllowedCallersClaimsValidator
from adapter_with_error_handler import AdapterWithErrorHandler

CONFIG = DefaultConfig()
CLAIMS_VALIDATOR = AllowedCallersClaimsValidator(CONFIG)
AUTH_CONFIG = AuthenticationConfiguration(
    claims_validator=CLAIMS_VALIDATOR.claims_validator
)
# Create adapter.
# See https://aka.ms/about-bot-adapter to learn more about how bots work.
SETTINGS = ConfigurationBotFrameworkAuthentication(
    CONFIG,
    auth_configuration=AUTH_CONFIG,
)
ADAPTER = AdapterWithErrorHandler(SETTINGS)
BOT = GenieBot(CONFIG)


async def messages(req: Request) -> Response:
    return await ADAPTER.process(req, BOT)

APP = web.Application()
APP.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    try:
        web.run_app(APP, host="localhost", port=CONFIG.PORT)
    except Exception as error:
        raise error