#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
from typing import Dict
from botbuilder.core.skills import BotFrameworkSkill


class DefaultConfig:
    """ Bot Configuration """

    def __init__(self, env, bot_prefix) -> None:
        self.env = env
        self.SKILL_HOST_ENDPOINT = self.envs[self.env]["endpoint"]
        self.SKILLS = [
        {
            "id": "SkillBot",
            "app_id": "5afff072-da4e-4ba2-9e3e-6b8a79554967",
            "skill_endpoint": f'http://{self.get_env_key("skill_bot_url")}/api/messages',
        },
    ]
        if bot_prefix is not None:
            self.BOT_PREFIX = bot_prefix
    
    def get_env_key(self, key):
        return self.envs[self.env][key]

    env = "prod"
    BOT_PREFIX=os.environ.get("BOT_PREFIX", "genie")
    
    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    APP_TYPE = "MultiTenant"
    APP_TENANTID = os.environ.get("MicrosoftAppTenantId", "")
    CONNECTION_NAME = "Teams Oauth" # os.environ.get("ConnectionName", "Teams Oauth")
    
    envs = { 
                "local-to-prod" : {
            "endpoint" : f"http://localhost:{PORT}/api/skills",
             "skill_bot_url" : f"{BOT_PREFIX}-genie-skill-001.azurewebsites.net"
        },
        "prod" : {
            "endpoint" : f"http://{BOT_PREFIX}-geniebot-001.azurewebsites.net/api/skills",
             "skill_bot_url" : f"{BOT_PREFIX}-genie-skill-001.azurewebsites.net"
        },
         "local" : {
            "endpoint" : f"http://localhost:{PORT}/api/skills",
             "skill_bot_url" : "localhost:39783"
        }
    }

    SKILL_HOST_ENDPOINT = None
    SKILLS = [
        {
            "id": "SkillBot",
            "app_id": "5afff072-da4e-4ba2-9e3e-6b8a79554967",
            "skill_endpoint": f'http://localhost:39783/api/messages',
        },
    ]

    ALLOWED_CALLERS = os.environ.get("AllowedCallers", ["*"])


class SkillConfiguration:
    SKILL_HOST_ENDPOINT = DefaultConfig.SKILL_HOST_ENDPOINT
    SKILLS: Dict[str, BotFrameworkSkill] = {
        skill["id"]: BotFrameworkSkill(**skill) for skill in DefaultConfig.SKILLS
    }
