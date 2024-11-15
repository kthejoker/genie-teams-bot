# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import ActivityHandler, MessageFactory, TurnContext
from botbuilder.schema import Activity, ActivityTypes, EndOfConversationCodes
from botbuilder.core import BotFrameworkAdapterSettings, BotFrameworkAdapter, ActivityHandler, TurnContext
from botbuilder.schema import Activity, ChannelAccount
import requests
import time

class GenieBot(ActivityHandler):
    def __init__(self, CONFIG):
        self.conversation_ids = {}
        self.CONFIG = CONFIG

    async def on_message_activity(self, turn_context: TurnContext):
        question = turn_context.activity.text
        user_id = turn_context.activity.from_property.id

        conversation_id = self.conversation_ids.get(user_id)

        conversation_id, status, query_results = self.genie_conversation(
            self.CONFIG.DATABRICKS_SPACE_ID,
            self.CONFIG.DATABRICKS_HOST,
            self.CONFIG.DATABRICKS_TOKEN,
            question,
            conversation_id
        )

        if conversation_id is None:
            await turn_context.send_activity("Error: Unable to start or continue the conversation.")
            return

        self.conversation_ids[user_id] = conversation_id

        response = f"## Question\n\n{question}\n\n"

        if status:
            #content = status.get('content', 'N/A')
            #response += f"## Content\n\n{content}\n\n"
    
            if 'attachments' in status and status['attachments']:
                attachment = status['attachments'][0]
                if 'query' in attachment:
                    description = attachment['query'].get('description', 'N/A')
                    response += f"## Description\n\n{description}\n\n"
                elif 'text' in attachment:
                    text_content = attachment['text'].get('content', '')
                    response += f"## Clarification\n\n{text_content}\n\n"
                    
                    await turn_context.send_activity(response)
                    return  # Exit the function here
    
        if query_results and 'statement_response' in query_results:
            result = query_results['statement_response']
            if 'result' in result and 'data_typed_array' in result['result']:
                data = result['result']['data_typed_array']
                schema = result['manifest']['schema']['columns']
                
                response += "## Query Results\n\n"
                
                header = "| " + " | ".join(col['name'] for col in schema) + " |"
                separator = "|" + "|".join(["---" for _ in schema]) + "|"
                
                response += header + "\n" + separator + "\n"
                
                for row in data:
                    formatted_row = []
                    for value, col_schema in zip(row['values'], schema):
                        if value is None or value.get('str') is None:
                            formatted_value = "NULL"
                        elif col_schema['type_name'] in ['DECIMAL', 'DOUBLE', 'FLOAT']:
                            formatted_value = f"{float(value['str']):,.2f}"
                        elif col_schema['type_name'] in ['INT', 'BIGINT']:
                            formatted_value = f"{int(value['str']):,}"
                        else:
                            formatted_value = value['str']
                        formatted_row.append(formatted_value)
                    response += "| " + " | ".join(formatted_row) + " |\n"

                await turn_context.send_activity(response)

    async def on_members_added_activity(
        self, members_added: [ChannelAccount], turn_context: TurnContext
    ):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Welcome to the Genie Conversation Bot!")


    def genie_conversation(self, space_id, host, token, question, conversation_id=None):
        headers = {'Authorization': f'Bearer {token}'}

        def start_conversation(question):
            url = f"{host}/api/2.0/genie/spaces/{space_id}/start-conversation"
            payload = {"content": question}
            response = requests.post(url, json=payload, headers=headers)
            return response.json()

        def create_follow_up_message(conversation_id, question):
            url = f"{host}/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages"
            payload = {"content": question}
            response = requests.post(url, json=payload, headers=headers)
            return response.json()

        def get_message_status(conversation_id, message_id):
            url = f"{host}/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}"
            response = requests.get(url, headers=headers)
            return response.json()

        def get_query_results(conversation_id, message_id):
            url = f"{host}/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}/query-result"
            response = requests.get(url, headers=headers)
            return response.json()

        def process_message(conversation_id, message_id):
            while True:
                status = get_message_status(conversation_id, message_id)
                if 'status' not in status:
                    print("Error: Unexpected response format:", status)
                    return None, None
                if status['status'] == 'COMPLETED':
                    if 'attachments' in status and status['attachments']:
                        attachment = status['attachments'][0]
                        if 'text' in attachment:
                            # Return the clarification question instead of query results
                            return status, {'clarification': attachment['text']['content']}

                    query_results = get_query_results(conversation_id, message_id)
                    return status, query_results
                elif status['status'] == 'EXECUTING_QUERY':
                    results = get_query_results(conversation_id, message_id)
                    if 'status' in results and 'state' in results['status']:
                        if results['status']['state'] == 'SUCCEEDED':
                            return results, results
                time.sleep(2)

        if conversation_id is None:
            conversation = start_conversation(question)
            if 'conversation_id' not in conversation or 'message_id' not in conversation:
                print("Error: Unable to start conversation. API response:", conversation)
                return None, None, None
            conversation_id = conversation['conversation_id']
            message_id = conversation['message_id']
        else:
            follow_up = create_follow_up_message(conversation_id, question)
            if 'id' not in follow_up:
                print("Error: Unexpected response format for follow-up message. API response:", follow_up)
                return None, None, None
            message_id = follow_up['id']

        status, query_results = process_message(conversation_id, message_id)
        return conversation_id, status, query_results
