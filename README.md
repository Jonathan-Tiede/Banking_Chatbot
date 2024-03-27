# Building A Banking Chatbot Using Google's Dialogflow NLP Model
## Objective
With cloud computing becoming mainstream, its reach knows almost no bounds. It is a technology that many in the industry should learn and benefit from. This is my foray into cloud technologies using Google's Dialogflow; a natural language processing (NLP) AI centered around user/AI interaction... a chatbot. Dialogflow has a very user-friendly interface, intuitive design and enough options available to cater to many company's or people's needs. When paired with a backend server such as FastAPI, the interactivity truly becomes limitless.

Using Dialogflow as the frontend, FastAPI as the backend server, PostgreSQL as the database, and website hosting tools such as Uvicorn and Ngrok, I created a banking chatbot.

The high-level goal for this project is to learn cloud-based NLP software and its interactions with backend servers and database access/management. Second, the bot will be able to interact with users to accomplish any number of objectives such as open new bank accounts; interact with existing bank accounts by checking account balances, depositing, and withdrawing funds; and to check bank branch information such as hours of operation, locations, and phone numbers. The chatbot will be hosted to a basic website for easy deployment to the masses.

The following explanations will walk you through the development of the bot, explain any interactions, and where applicable discuss any issues encountered during the process.
## Project Plan
### Google's Dialogflow: Cloud-Based, Pre-Trained NLP Platform (DONE)
Dialogflow is a state-of-the-art conversational AI with an intuitive interface and plenty of options to meet the needs of customers such as Google, Domino's Pizza, Ticketmaster, and Lufthansa Airlines. 

Due to its initial ease of use and integration into a FastAPI server, Dialogflow has been selected over its competitors, such as Amazon Lex, IBM Watson Assistant, and Rasa. Dialogflow also has a limited free option for their CX (advanced) edition. For these reasons, Dialogflow was selected.
#### Intent & Context
Like many other conversational AI's, Dialogflow uses the standardized "intent/context" system where, based on the training phrases, the model determines the user's intent (action, question, desire, etc.). It might then ask for information or send data to the backend server in the form a JSON response. 

Most people will need to interact with the bot more than once per conversation. This is where "context" comes in. Context, here, refers to the ability to manage the state of the current conversation across multiple interactions; ie. to direct the flow of the conversation in a more sensical manor. With the proper context set, the bot is able to more accurately predict the intent of the user. For example, it wouldn't make sense for a user to ask a chatbot to remove an item from the cart if the user hasn't already added at least one item to the cart.

With each intent put into the correct context, the chatbot is better able to understand the conversation and more accurately and efficiently serve the needs of the user.

In the case of this banking chatbot, an example of an appropriately contextualized intent might be:

![[Pasted image 20240327165439.png]]

Where *"accountexisting-followup"* refers to any upstream intent which has this as the output context. Similarly, *"accountexisting-contextget_info-followup"* drives the bot to any intent downstream that has this as the input context. Here, the bot will know to prioritize the intents with corresponding contexts when looking at the training phrases during the classification step within the model.
#### Training Phrases
Each intent also contains a set of training phrases and responses. As the model grows in complexity, it becomes increasingly more important to ensure a diverse, yet accurate, set of phrases upon which the model can learn. 

One such instance of this ambiguity occurred early on where the bot was prompted to make a withdrawal (even using the word "withdrawal" in the user prompt) and yet the bot understood the request to mean the user wanted to make a deposit. The training phrases in the *withdrawal* intent did not contain the word *"deposit"* (and similarly for the deposit intent). It was more nuanced than that. The way the request to Dialogflow was worded more closely matched the wording of a few training phrases in the deposit intent and so, despite the keyword (withdrawal), the bot was confused. This was fairly easily rectified by increasing the training phrase pool size for both intents.
### FastAPI: Backend Server
The necessary backend server is quite straight forward. At a high level, it contains only three sections:

1. The route (to which the server/chatbot points to).
2. Stripping information from the received JSON payload.
3. Directing each webhook call to the correct function based on the model's perceived user intent.
#### The Routing
In FastAPI, `@app.post("/")` is a decorator used to define a route that handles POST requests on the root path ("/") of the web application. A POST request is one where data is being sent to the server from the client (Dialogflow, web browser, etc.).

1. **`@app.post`:** This is a Python decorator provided by FastAPI. Decorators are a way to modify the behavior of functions or methods. In FastAPI, `@app.post` is used to define a route that handles POST requests. It's attached to a function that will be executed when the specified route is accessed via a POST request.
2. **`("/")`:** This specifies the URL path for the route. In this case, `"/"` represents the root path of the web application. This means the route defined by `@app.post("/")` will be accessed when the root URL of the web application is requested via a POST method.

So, when you see `@app.post("/")`, it means the decorated function underneath it will be executed when a POST request is made to the root path ("/") of the web application. Generally, the decorated function would handle the logic of the POST request directly.
#### JSON Payload
Once the server has received the incoming data from Dialogflow, which is in the form of a JSON file, the payload is stripped of anything required to properly handle the intent's logic. Here, four slices of the payload are required:

```
intent = payload['queryResult']['intent']['displayName']
parameters = payload['queryResult']['parameter']
output_contexts = payload['queryResult']['outputContexts']
session_id = re.search(r"/session/(.*?)/contexts/, output_contexts[0]['name']).group(1)
```
#### Handling User Intent
Based on the model's predicted intent, the payload data above is passed through the correct function. As of now, the following functions exist:

1. new_account()
2. account_login()
3. account_withdrawal()
4. account_deposit()
5. account_balance()

Each function serves a unique, and obvious, purpose in connecting the user to the banks database.
### PostgreSQL: Bank Database (DONE)
The SQL server is basic but can be scaled to any level of functionality or intricacy in a straightforward way.

Presently, two tables exist:

|  Column Name  |   Type    |
| :-----------: | :-------: |
|      id       | bigserial |
|  first_name   |  varchar  |
|   last_name   |  varchar  |
| date_of_birth |   date    |
|      pin      |   int4    |

and

|  Column Name   |  Type  |
| :------------: | :----: |
|       id       |  int4  |
|    balance     | float8 |
|  num_deposit   |  int4  |
| num_withdrawal |  int4  |

A connection to the database is made during each of the following Dialogflow intents and closed just as soon as the queries are committed:
- account.new - context: get_info
- account.existing - context: get_info
- account.existing - context: check_balance
- account.existing - context: withdraw
- account.existing - context: deposit

The connection call is fairly straightforward:

```
def connection(config):
	try:
		conn = psycopg2.connect(**config)
		return conn
	except (psycopg2.DatabaseError, Exception) as error:
		print(error)
```

where `config` refers to a file `configuration.ini` containing the connection variables.

Once logged in, some base SQL queries are made to interact with the user's account. One such query is two-fold: first obtain account balance and then update balance with deposit amount:

```
SELECT balance FROM accountholder h
LEFT JOIN accountinfo i
ON h.id = i.id
WHERE pin=%s AND first_name=%s AND last_name=%s;

UPDATE accountinfo SET balance=%s 
WHERE id=
	(SELECT id FROM accountholder
	WHERE first_name=%s AND last_name=%s AND pin=%s);
```
## Execution
To run this chatbot the following steps must be executed in order:
1. Initialized Uvicorn in your terminal. Ensure you are in the working directory for main.py --> `uvicorn app:main --reload.` This will watch for any updates to the main.py file and will host the server to localhost:8000. If any updates are made, the server is automatically reloaded.![[Pasted image 20240327141041.png]]
3. Run Ngrok in your terminal with `ngrok http 8000.` If different, replace the 8000 port with your localhost port from step 1. This will open a secure tunnel where localhost:8000 can be forwarded. An example of the secure connection is: "https://8bce-2600-387-f-6719-00-5.ngrok-free.app" ![[Pasted image 20240327141540.png]]
4. Open your Dialogflow account, navigate to your working project agent, select "Fulfillment" on the left hand side and enter the Ngrok *forwarding* address in the *URL* space. ![[Pasted image 20240327141651.png]]
6. Ensure the PostgreSQL (or equivalent) database is running. ![[Pasted image 20240327141736.png]]
7. Now you can interact with the chatbot through the "Try it now" window in the upper right-hand side.
8. At a later date, the chatbot interaction will accessible through a basic website. 
## Next Steps
In its current state, the chatbot is capable of handling any client request under a strictly ideal set of conditions (reasonably well worded requests, correct answers to prompts, etc.).

The following is a non-exhaustive list of features/functionalities yet to be implemented:
- Handle poorly phrased requests --> Train model on additional expected phrases.
- Addition of request confirmations --> Additional intents focused on yes/no answers. Database should update only upon request confirmation.
- Handling unexpected disconnections or nonsensical context chains mid request --> Backend server management of Dialogflow JSON responses. Incoming intents should match expected incoming intents.
- Bank branch information (hours, ph#, address, etc.)
- Deployment to example website
- Create chatbot model using **PyTorch** to replace Dialogflow
## Skills Gained
- **Dialogflow** (along with industry standard terminology and concepts applicable to many cloud-based NLP models).
- Server creation and frontend connection through **FastAPI**.
- **PostgreSQL** database hosted on my local machine for all data management.
- **Uvicorn** to host asynchronous web applications. Since FastAPI is an asynchronous framework, Uvicorn is a natural selection.
- Dialogflow requires a secure server connection. **Ngrok** creates a secure tunnel to localhost enabling deployment of a localhost server to the internet without the need of a public or remote server.