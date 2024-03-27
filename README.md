# Banking Chatbot
## Objective (DONE)
With cloud computing becoming mainstream, its reach knows almost no bounds. It is a technology that many in the industry should learn and benefit from. This is my foray into cloud technologies using Google's Dialogflow; a natural language processing (NLP) AI centered around user/AI interaction... a chatbot. Dialogflow has a very user-friendly interface, intuitive design and plenty of options available to cater to many company's and people's needs. When paired with a bankend server such as FastAPI, the interactivity truly becomes limitless.

Using Dialogflow as the frontend, FastAPI as the backend server, PostgreSQL as the database, and website hosting tools such as Uvicorn and Ngrok, I created a banking chatbot. 

The high-level goal for this project is to learn cloud-based NLP software and its interactions with backend servers and database access/management. Second, the bot will be able to interact with users to accomplish any number of objectives such as open new bank accounts; interact with existing bank accounts by checking account balances, depositing, and withdrawing funds; and to check bank branch information such as hours of operation, locations, and phone numbers. The chatbot will be hosted to a basic website for easy deployment to the masses.

The following explanations will walk you through the development of the bot, explain any interactions, and where applicable discuss any issues encountered during the process.


## Project Plan
### Google's DialogFlow: Cloud-Based, Pre-Trained NLP Model
- Why DialogFlow?
- Discuss high-level structure of DialogFlow
    - Intents, context, context lifespan, webhooks
- Discuss other relavent information such as:
    - Training phrase accuracy (what issues did I have: asking to deposit money led to withdrawing money due to inaccurate phrases)

### FastAPI: Backend Server
- Discuss Uvicorn and ngrok
- Discuss how DialogFlow and FastAPI communicate using JSON responses via intents with webhooks turned on
- Discuss high-level flow of backend server (if statements, helper functions, etc.)

### PostgreSQL: Bank Database
- Discuss format of database (2 tables with XYZ columns)
- Discuss how FastAPI server connected to database
- Include some SQL code snippets


## Next Steps (DONE)
In its current state (as of 03/26/24), the chatbot is capable of handling any client request under a strictly ideal set of conditions (reasonably well worded requests, correct answers to prompts, etc.). The following is a non-exhaustive list of features/functionalities yet to be implemented:
- Handle poorly phrased requests --> Train model on additional expected phrases.
- Addition of request confirmations --> Additional intents focused on yes/no answers. Database should update only upon request confirmation.
- Handling unexpected disconnections or nonsensical context chains mid request --> Backend server management of Dialogflow JSON responses. Incoming intents should match expected incoming intents.
- Bank branch information (hours, ph#, address, etc.)
- Deployment to website
- Deployment to desktop application using **PySide6** or **Tkinter**


## Skills Gained (DONE)
- **Dialogflow** (along with industry standard terminology and concepts applicable to many cloud-based NLP models).
- Server creation and front-end connection through **FastAPI**.
- **PostgreSQL** database hosted on my local machine for all data management.
- **Uvicorn** to host asynchronous web applications. Since FastAPI is an asynchronous framework, Uvicorn is a natural selection.
- Dialogflow requires a secure server connection. **Ngrok** creates a secure tunnel to localhost enabling deployment of a localhost server to the internet without the need of a public or remote server.