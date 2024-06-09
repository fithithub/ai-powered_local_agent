# Streamlit app based on Langchain agents using the OpenAI models.

The purpose of this app is to show the capabilities of AI agents when these have access to external tools. These tools allow LLMs to perform actions "in the real world".

The difference with written code that manually differentiates between cases or code that leads the flow of the execution is that in this situation (agents with tools) the agent decides on his own which tools (zero or more) are necessary for performing the task at hand. No programming is required beyond creating the tool and the agent.

The agents are told in natural language how and when to use the tools. These tools that perform actions can be as simple as sending an email, modifying files, deciding what to do next based on the current context or even coding on a REPL. All these situations are displayed in the app. Even the "knowledge" of the LLM/agent can be further expanded by automatically accessing databases, files or web pages.

### **Usage**:  
Two options are available: prompting the agent to perform tasks or deleting the chat history (and the agent's memory). The memory of the agent, in any case, is virtual and does not last for subsequent executions. The actions that the agent can do are elaborated below.

### **Tools**:  
- *TableRetriever*: reads a table, either the one containing information of the stock and items or the one containing the record of orders of clients.  
- *StockUpdate*: updates the stock of a given item. It can be the result of either a purchase or a sale.  
- *OrdersUpdate*: adds a new record in the table of previous orders. Additionally the agent should call the *StockUpdate* too.
- *SendMail*: sends an email. The fields "to" and "from" are hardcoded from the *.env* file for security and privacy reasons (EMAIL_ADDRESS = "name@gmail.com", EMAIL_PASSWORD = "XXXX"). 
- *PerformAnalysis*: asks the agent to use the REPL for executing actions that were not provided as tools, such as calculating statistics from the table orders, visualizing the results, and storing them in a folder. It could seem "redundant" but it actually provides robustness to the prompts.
- *GetWeather*: a discount may be given to clients that apply for it. The condition is that, at the time and place they are applying for the discount, the weather must be grim. In that case, an email is sent to the client explaining how to obtain the markdown, pun intended.  
- *EasterEgg*: if the user claims to be the lord the teas, T, the agent's discourse changes.

#### **Note**:
 - **From the root of the directory, run the app using the command *streamlit run app.py**
 - **A *.env* file must exist at the root of the directory and it must have the appropriate values (OPENAI_API_KEY="sk-XXXX...") for the correct functioning of the app.**
 - **Use the *requirements.txt* or *environment.yml* file in the *requirements* folder for installing the Python packages.**
 - **The Python version is 3.11.0.**
 - **Conda 24.1.2 was used for the generation of the environment and the development of the app.**
 - **This work is part of my Master's Thesis.**