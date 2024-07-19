import os
import sys
import traceback

from botbuilder.core import MemoryStorage, TurnContext
from teams import Application, ApplicationOptions, TeamsAdapter
from teams.ai import AIOptions
from teams.ai.models import AzureOpenAIModelOptions, OpenAIModel, OpenAIModelOptions
from teams.ai.planners import ActionPlanner, ActionPlannerOptions
from teams.ai.prompts import PromptManager, PromptManagerOptions
from teams.state import TurnState

from chat_completion_model import CustomChatCompletionModel, CustomChatCompletionModelOptions
from config import Config

config = Config()

# Create AI components
model: CustomChatCompletionModel

model = CustomChatCompletionModel(
    CustomChatCompletionModelOptions(
        api_key=config.API_KEY,
        endpoint=config.ENDPOINT,
    )
)
    
prompts = PromptManager(PromptManagerOptions(prompts_folder=f"{os.getcwd()}/prompts"))

planner = ActionPlanner(
    ActionPlannerOptions(model=model, prompts=prompts, default_prompt="chat")
)

# Define storage and application
storage = MemoryStorage()
try:
    bot_app = Application[TurnState](
        ApplicationOptions(
            bot_app_id=config.APP_ID,
            storage=storage,
            adapter=TeamsAdapter(config),
            ai=AIOptions(planner=planner),
        )
    )
except Exception as e:
    print(f"Error: {e}")

@bot_app.conversation_update("membersAdded")
async def on_members_added(context: TurnContext, state: TurnState):
    await context.send_activity("How can I help you today?")

@bot_app.error
async def on_error(context: TurnContext, error: Exception):
    # This check writes out errors to console log .vs. app insights.
    # NOTE: In production environment, you should consider logging this to Azure
    #       application insights.
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()

    # Send a message to the user
    await context.send_activity("The bot encountered an error or bug.")