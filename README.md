# Overview of the Custom Model Sample

Welcome to our sample application, designed to demonstrate the flexibility and power of integrating AI models into your projects. This app is built to work seamlessly with both remote and local AI models, providing a versatile platform for developing AI-powered applications.

## Features

- **Support for Remote Models**: Leverage the capabilities of advanced AI models hosted on remote servers, such as Azure AI Studio. This option is ideal for those looking to utilize cloud-based AI services for enhanced performance and scalability.
- **Integration with Local Models**: For users who prefer or require running AI models locally, this app supports integration with local models, including transformer pre-trained models. This is particularly useful for development and testing purposes, or when operating in environments with limited internet access.


## Get started with the sample

> **Prerequisites**
>
> To run the sample in your local dev machine, you will need:
>
> - [Python](https://www.python.org/), version 3.8 to 3.11.
> - [Python extension](https://code.visualstudio.com/docs/languages/python), version v2024.0.1 or higher.
> - [Teams Toolkit Visual Studio Code Extension](https://aka.ms/teams-toolkit) latest version or [Teams Toolkit CLI](https://aka.ms/teams-toolkit-cli).
> - An account with [Azure OpenAI](https://aka.ms/oai/access).
> - A [Microsoft 365 account for development](https://docs.microsoft.com/microsoftteams/platform/toolkit/accounts).

### Configurations
1. Open the command box and enter `Python: Create Environment` to create and activate your desired virtual environment. Remember to select `src/requirements.txt` as dependencies to install when creating the virtual environment.

* **Configuring for Remote Models**

    If you're using a remote model, you'll need to provide your API key and endpoint so the app can communicate with the model. Here's how:

    1. Open the file `env/.env.local.user` in your project directory.
    2. Fill in your API key and endpoint details as follows:
        ```
        API_KEY=your_api_key_here,
        ENDPOINT=your_model_endpoint_here
        ```
* **Configuring for Local Models**

    For those opting to use a local model, the setup is just as straightforward:

    1. Run `python src/local_model_server.py` in root folder to start a local model internal server.
    2. Open the file `env/.env.local.user` in your project directory.
    3. To configure the app to use a local model, enter the following details:
        ```
        SECRET_API_KEY='fake_key',
        ENDPOINT='http://127.0.0.1:3979/generate'
        ```
    This configuration tells the app to communicate with a local server running on your machine, simulating the behavior of a remote AI model but with the convenience and privacy of local execution.

### Conversation with bot
1. Select the Teams Toolkit icon on the left in the VS Code toolbar.
1. In the Account section, sign in with your [Microsoft 365 account](https://docs.microsoft.com/microsoftteams/platform/toolkit/accounts) if you haven't already.
1. Press F5 to start debugging which launches your app in Teams using a web browser. Select `Debug in Teams (Edge)` or `Debug in Teams (Chrome)`.
1. When Teams launches in the browser, select the Add button in the dialog to install your app to Teams.
1. You will receive a welcome message from the bot, or send any message to get a response.

**Congratulations**! You are running an application that can now interact with users in Teams:

> For local debugging using Teams Toolkit CLI, you need to do some extra steps described in [Set up your Teams Toolkit CLI for local debugging](https://aka.ms/teamsfx-cli-debugging).

![ai chat bot](https://user-images.githubusercontent.com/7642967/258726187-8306610b-579e-4301-872b-1b5e85141eff.png)

## Extend the sample

You can follow [Build a Custom Model Bot Sample in Teams](https://aka.ms/teamsfx-basic-ai-chatbot) to extend the Custom Model Bot sample with more AI capabilities, like:
- [Customize prompt](https://aka.ms/teamsfx-basic-ai-chatbot#customize-prompt)
- [Customize user input](https://aka.ms/teamsfx-basic-ai-chatbot#customize-user-input)
- [Customize conversation history](https://aka.ms/teamsfx-basic-ai-chatbot#customize-conversation-history)
- [Customize model type](https://aka.ms/teamsfx-basic-ai-chatbot#customize-model-type)
- [Customize model parameters](https://aka.ms/teamsfx-basic-ai-chatbot#customize-model-parameters)
- [Handle messages with image](https://aka.ms/teamsfx-basic-ai-chatbot#handle-messages-with-image)

## Additional information and references

- [Teams Toolkit Documentations](https://docs.microsoft.com/microsoftteams/platform/toolkit/teams-toolkit-fundamentals)
- [Teams Toolkit CLI](https://aka.ms/teamsfx-toolkit-cli)
- [Teams Toolkit Samples](https://github.com/OfficeDev/TeamsFx-Samples)

## Known issue
- If you use `Debug in Test Tool` to local debug, you might get an error `InternalServiceError: connect ECONNREFUSED 127.0.0.1:3978` in Test Tool log. You can wait for Python launch console ready and then refresh the front end web page. 
- When you use `Launch Remote in Teams` to remote debug after deployment, you might loose interaction with your bot. This is because the remote service needs to restart. Please wait for several minutes to retry it. 