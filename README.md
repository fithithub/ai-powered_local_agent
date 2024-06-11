# Streamlit app based on Langchain agents using the OpenAI models.

The purpose of this app is to show the capabilities of AI agents when these have access to external tools. These tools allow LLMs to perform actions "in the real world".

The difference with written code that manually differentiates between cases or code that leads the flow of the execution is that in this situation (agents with tools) the agent decides on his own which tools (zero or more) are necessary for performing the task at hand. No programming is required beyond creating the tool and the agent.

The agents are told in natural language how and when to use the tools. These tools that perform actions can be as simple as sending an email, modifying files, deciding what to do next based on the current context or even coding on a REPL. All these situations are displayed in the app. Even the "knowledge" of the LLM/agent can be further expanded by automatically accessing databases, files or web pages.

Specifically, this code is a provides evidence on how an agent could help a clerk on a tea shop.

### **Structure**:
The repository needs the *app.py* file for running the streamlit application and the *tools.py* file for the tools. These are loaded from the *app.py*. Additionally, the two excels, *orders.xlsx* and *stock.xlsx* contain information about the stock and the client orders/purchases.

The columns for the *stock* table are the name of the product, the number of current units, the supplier, the category of the product (tea, coffe or herbal tea), the selling price per unit and the number of total sales up to date.

The fields of the *orders* table are the name of the client who made the order, the product purchased, the number of units bought and the total cost of the order. Note that the arrangement of the table forces a single purchase of different products to be registered as different purchases each of a distinct product.

Furthermore, an *imgs* folder is placed for special ocasions (when the agent generates a plot and saves it). 

It is possible to glance at the application without running it thanks to the *examples* folder. This one is divided into two subfolders. The *external_applications* folder showcases how the agent uses external apps such as emails or web pages. The *local_applications* folder contains examples of modifications and creation of local files. Both subfolders contain images and videos displaying the potential of the app. 

The requirements folder contains the needed packages and libraries.

### **Usage**:  
 - Install the Python packages and libraries from the *requirements.txt* or *environment.yml* file in the *requirements* folder.
 - From the root of the directory, run the app using the command *streamlit run app.py*.
 - A *.env* file must exist at the root of the directory and it must have the appropriate values (OPENAI_API_KEY="sk-XXXX...") for the correct functioning of the app. Furthermore, the tool *SendMail* also requires two more variables to be in this file.

When running the app, at the bottom the user can prompt the agent to perform tasks and the conversation will begin as a normal chatbot would do. There is an option at the top left for deleting the chat history (and the agent's memory). The memory of the agent, in any case, is virtual and does not last for subsequent executions. The actions that the agent can do are elaborated below.

### **Tools**:  
- *TableRetriever*: reads a table, either the one containing information of the stock and items or the one containing the record of orders of clients.  
- *StockUpdate*: updates the stock of a given item. It can be the result of either a purchase or a sale.  
- *OrdersUpdate*: adds a new record in the table of previous orders. Additionally the agent should call the *StockUpdate* too.
- *SendMail*: sends an email. The field "from" and the password for the login should be hardcoded in the *.env* file for security reasons (EMAIL_ADDRESS = "name@gmail.com", EMAIL_PASSWORD = "XXXX"). 
- *PerformAnalysis*: asks the agent to use the REPL for executing actions that were not provided as tools, such as calculating statistics from the table orders, visualizing the results, and storing them in a folder. It could seem "redundant" but it actually provides robustness to the prompts.
- *GetWeather*: a discount may be given to clients that apply for it. The condition is that, at the time and place they are applying for the discount, the weather must be grim. In that case, an email is sent to the client explaining how to obtain the markdown, pun intended.  
- *EasterEgg*: if the user claims to be the lord the teas, T, the agent's discourse changes.

#### **Note**:
 - **The Python version is 3.11.0.**
 - **Conda 24.1.2 was used for the generation of the environment and the development of the app.**
 - **This work is part of my Master's Thesis.**
