# tools: 
# TableRetriever, StockUpdate, OrdersUpdate, SendMail, PerformAnalysis, GetWeather, EasterEgg

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import StructuredTool
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
import openai

# LLMs, GPT3.5 Turbo
openai.api_key = os.environ["OPENAI_API_KEY"]
from langchain_openai import ChatOpenAI

llm_35 = ChatOpenAI(model_name="gpt-3.5-turbo")
llm_4 = ChatOpenAI(model_name="gpt-4-turbo-preview")
llm_4o = ChatOpenAI(model_name="gpt-4o")


############################################################################################################


# Tool - TableRetriever: Retrieve a table, either the stock.xlsx or orders.xlsx.
# The agent can use it to know information about the tables.

# Schema
# Where the inputs for the tool are defined for the agent
class RetrieveTableInput(BaseModel):
    table_name: str = Field(description="Name_of_table.xlsx")

# Function
# The function that must execute when the agent calls the tool
def retrieve_table(table_name: str) -> pd.DataFrame:
    query=table_name
    df = pd.read_excel(query)
    return df

# Tool
# The complete tool, containing the function to execute, its name, a description for the agent to understand how and when to use it,
# the inputs, and a special parameter for either finishing the flow when the tool executes or allowing the agent to use more tool
table_retriever = StructuredTool.from_function(
    func=retrieve_table,
    name="TableRetriever",
    description="""
    Displays a table from a database as a pandas dataframe.
    Use this tool for retrieving table's data.
    The two accessible tables are stock.xlsx and orders.xlsx.
    If the user talks about products, stock, or wants to know the available coffees and teas, show the\
    stock.xlsx table. If the user wants to know about orders or something similar, \
    show the orders.xlsx table.
    """,
    args_schema=RetrieveTableInput,
    return_direct=False,
)


############################################################################################################


# Tool - StockUpdate: Updates the stock of the products table.
# The agent enters the product, the interaction (either buy or sale) or the quantity.
# Then the appropriate changes happen automatically thanks to the tool.
# When buying, the number of units updates but in the case of selling, the 'Accumulated sales' value must be updated too.
# If less than 10 units are left, the agent warns the user

# Schema
class StockUpdateInput(BaseModel):
    quantity: int = Field(description="Amount of stock to update.")
    product_name: str = Field(description="Name of the product to update the stock for.")
    interaction: str = Field(description="Type of interaction. Can be 'sale' or 'buy'.")

# Function
def update_stock(quantity:int, product_name:str, interaction:str):
    product_name=product_name.lower()
    df=pd.read_excel('stock.xlsx')
    if interaction not in ["buy", "sale"]:
        return "Notify the user that the only possible interactions are 'buy' or 'sale'."
    elif interaction == "buy":
        df.loc[df['Product'] == product_name, 'Units'] = df.loc[df['Product'] == product_name, 'Units'].iloc[0] + quantity
    elif interaction == "sale":
        df.loc[df['Product'] == product_name, 'Units'] = df.loc[df['Product'] == product_name, 'Units'].iloc[0] - quantity
        df.loc[df['Product'] == product_name, 'Accumulated sales'] = df.loc[df['Product'] == product_name, 'Accumulated sales'].iloc[0] + quantity

    if df.loc[df['Product'] == product_name, 'Units'].iloc[0] < 10:
        vendor_name = df.loc[df['Product'] == product_name, 'Supplier'].iloc[0]

        # A new table could be created in case the file cannot be overwritten
        df.to_excel('stock.xlsx', index=False)
        return f"""Say that the table has been updated correctly, but warn \
            the user that there is little stock left of {product_name}. Remind \
            them that their supplier for this product is {vendor_name} and recommend \
            placing an order."""
    else:
        df.to_excel('stock.xlsx', index=False)
        return "Say that the table has been updated correctly."

# Tool
stock_update = StructuredTool.from_function(
    func=update_stock,
    name="StockUpdate",
    description="Use this tool to update the stock column of the Products table. \
        Reasons for updating it may be that some products have been sold or an order has been received.\
            Make sure the name of the product exists in the table stock.xlsx.",
    args_schema=StockUpdateInput,
    return_direct=False,
)



############################################################################################################



# Tool - OrdersUpdate: Add a new order for a product in table orders
# The agent writes a new registry for a purchase, containig the name of the product, the quantity ordered and the name of the client.
# The total cost is calculated inside the tool as additional information.
# In the case of a sale, the agent is prompted to update the stock too. For this situation the parameter *return_direct* is critical

# Schema
class OrdersUpdateInput(BaseModel):
    product: str = Field(description="Name of the product")
    units: int = Field(description="Ordered quantity")
    name: str= Field(description="Name of the client")

# Function
def update_order_table(product,units,name):
    df=pd.read_excel('orders.xlsx')    
    df_2=pd.read_excel('stock.xlsx')
    product=product.lower().strip()

    # here we create a new row with the product, units, total price and name of the client
    update_row=[name,
                product,
                units,
                list(df_2[(df_2['Product']==product)]['Price'])[0]*units] # cost
    
    df.loc[len(df.index)]=update_row
    df.to_excel('orders.xlsx',index=False)
    return """Say that the table has been updated correctly.
In the case of a sale, you will update the stock by the same quantity using the StockUpdate tool. 
Remember you will need a name."""

# Tool
order_update = StructuredTool.from_function(
    func=update_order_table,
    name="OrdersUpdate",
    description="Use this tool to add a new order (sale) to the table orders. The name of the client, the product and the amount (units) \
        must be provided. Otherwise, first ask the user to provide the necessary information. I repeat, you need name, product and quantity.\
        Make sure the name of the product exists in the table stock.xlsx and it has the same name. Otherwise, check the stock table first.\
        If more than one product is named, divide the order into separate orders, one per product.",
    args_schema=OrdersUpdateInput,
    return_direct=False,
)


############################################################################################################

# Tool - SendMail: Sends an email (for security reasons, from and password are stored in environment variables)
# The agent can send an email when known the subject, body and receiver's email address.
# The agent can in some situations write the body and subject on its own, with basic instructions.

import smtplib
from email.message import EmailMessage

# Schema
class SendEmail(BaseModel):
    subject: str = Field(description="Subject of the email")
    body: str = Field(description="Body of the email")
    receiver: str = Field(description="Receiver's email address")

# Function
def send_email(subject, body,receiver):
    to=receiver
    from_email=os.environ["EMAIL_ADDRESS"]
    smtp_server="smtp.mail.yahoo.com" # SMTP server address, e.g., smtp.gmail.com for Gmail
    port=465
    login=os.environ["EMAIL_ADDRESS"]  # Your email address
    password=os.environ["EMAIL_PASSWORD"] # Your email password or app-specific password

    # Create the email message
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to

    # Send the email via SMTP server
    try:
        with smtplib.SMTP_SSL(smtp_server, port) as server:
            server.login(login, password)
            server.send_message(msg)
            print("Email sent successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")

# Tool
mail_sender = StructuredTool.from_function(
    func=send_email,
    name="SendMail",
    description="Use this tool for sending an email. Use it whenever you are told to and the necessary information is provided. Else ask for it.",
    args_schema=SendEmail,
    return_direct=False,
)


############################################################################################################


# Tool - PerformAnalyisis
# This tool returns guidelines to the agent, giving special robustness to prompts related to plotting images based on the data of the xlsx tables.
# This tool prompts the agent to use the prebuilt PythonREPLTool, which allows it to write and execute code on its own.
# The agent is asked for the name of the table to analyze, forcing it to see the names of the columns, 
# avoiding possible errors when executing code with the REPL.
# The prompt for the agent recommends using the folder *imgs* for storing images.

# Schema
class AnalysisSchema(BaseModel):
    table_name:str = Field(description="Name of the table to analyze")

# Function
def analysis(table_name:str):
    # file_path=os.path.join(wd,table_name)
    # df = pd.read_excel(file_path)
    df = pd.read_excel(table_name)
    return f"""Here is the beginning of the table that provides you with the structure:\n
    {df.head(3)}\n
    Now you must use the PythonREPLTool to achieve your objective:
    Remember that for using the df you must replace it with the following code
    pd.read_excel(os.path.join(wd,table_name))
    DO NOT USE df DIRECTLY UNDER ANY CIRCUMSTANCES
    for example, if you want to do df.cols, you will execute in the REPL:
    df = pd.read_excel(os.path.join(wd,table_name))
    and then
    df.cols
    You also NEED TO IMPORT the necessary libraries such as pandas and os.
    Whenever you create an image save it in the "imgs" folder and notify that the image has been saved by indicating the name.
    Furthermore, as the last step you must save the result of the Python execution for debuggin purposes.
    Always return a message when finishing the analysis.
"""

# Tool
do_analysis = StructuredTool.from_function(
    func=analysis,
    name="PerformAnalysis",
    description="""Use this tool to perform analysis of the data/tables stock and orders.\
    The two accessible tables are stock.xlsx and orders.xlsx.
    """,
    args_schema=AnalysisSchema,
    return_direct=False,
)


############################################################################################################


# Tool - GetWeather
# This tool is more complex, it outputs a prompt for the agent asking it to take decisions based on real time data.
# The agent inputs the city and country on which to check the weather and the tool returns the prompt plus the data.
# Read the output prompt from the function and the description of the tool for a deeper understanding.

# Schema
class WeatherSchema(BaseModel):
    city:str = Field(description="City to get the weather information")
    country:str = Field(description="Country to get the weather information")

# Function
def weather(city:str, country:str):
    city = city.lower().replace(" ", "-")
    country = country.lower().replace(" ", "-")
    
    url = f'https://www.timeanddate.com/weather/{country}/{city}'
    response = requests.get(url)

    if response.status_code != 200:
        return "URL unavailable."
    
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract temperature
    temperature = soup.find('div', class_='h2').text.strip()
    temperature = temperature.replace('\xa0', ' ')

    # Extract weather condition
    weather_condition = soup.find('div', id='qlook').find('p').text.strip()

    # Extracting humidity
    humidity_row = soup.find('th', text='Humidity').find_next_sibling('td')
    humidity = humidity_row.text.strip() if humidity_row else 'N/A'

    # Extracting wind
    wind_speed_row = soup.find('th', text='Wind Speed').find_next_sibling('td')
    wind_direction_row = soup.find('th', text='Wind Direction').find_next_sibling('td')
    wind = f"{wind_speed_row.text.strip()} {wind_direction_row.text.strip()}" if wind_speed_row and wind_direction_row else 'N/A'

    # print(f"Temperature: {temperature}")
    # print(f"Weather Condition: {weather_condition}")
    # print(f"Humidity: {humidity}")
    # print(f"Wind: {wind}")

    return f"""If the weather is bad, such as temperature < 15 ºC or wind > 40km/h, send an email to the client informing them on how to get the discount (1$). 
    Invent something for this part, such as subscribing to the newsletter. 
    Remember to send the email.
    Data you need for the mail (ask if necessary): name of the client and email.

    Before sending the email, show the body and subject to the user and ask for confirmation.
    Temperature: {temperature}
    Weather_condition: {weather_condition}
    Wind: {wind}
    """

# Tool
get_weather = StructuredTool.from_function(
    func=weather,
    name="GetWeather",
    description="""
    Whenever the user says a client is applying for a weather discount, use this tool.
    
    This tool allows you to access the weather conditions of a city.
    You shall ask for the city if it is not provided.
    """,
    args_schema=WeatherSchema,
    return_direct=False,
)


############################################################################################################


# Tool - Easter egg
# Some random bug for the agent. Desgined for entertainment purposes.
# Read the output prompt from the function and the description of the tool for a deeper understanding.

# Schema
class EESchema(BaseModel):
    the_what:str = Field(description="What does T want?")
    
# Function
def ee_func(the_what):
    return f"First and foremost, try to do what T wants, which is: {the_what}. \
        Then ask for an autograph and offer a cup of ancient tea. Also show absolute awe from now on. "

# Majestic Supreme Eternal Overlord of the Infinite Cosmos, Unparalleled Sovereign Ruler of the Multiverse, Grand Architect of the Boundless Universes, Exalted Commander of the Celestial Realms, Supreme Guardian of the Ethereal Dimensions, Divine Master and Protector of the Sacred Tea Leaves, Omnipotent Alchemist of the Celestial Tea Brews, Illustrious Holder of the Ancient Secrets of the Mystic Infusions, Timeless Custodian of the Sacred Tea Rituals, Revered Conductor of the Cosmic Harmony, and the Ultimate Embodiment of Wisdom and Power in the Eternal Quest for the Quintessential Tea Experience
# Tool
ee_tool = StructuredTool.from_function(
    func=ee_func,
    name="EasterEgg",
    # sadly, the description could not be as long as i would have liked
    description="""Use this tool if the person has claimed to be (in the last message) the only and one true god of tea (a.k.a. T), \
    whose ancient name is:
    Majestic Supreme Eternal Overlord of the Infinite Cosmos, Unparalleled Sovereign Ruler of the Multiverse, \
    Grand Architect of the Boundless Universes, Exalted Commander of the Celestial Realms, Supreme Guardian \
    of the Ethereal Dimensions, Divine Master and Protector of the Sacred Tea Leaves, Omnipotent Alchemist \
    of the Celestial Tea Brews, Illustrious Holder of the Ancient Secrets of the Mystic Infusions, Timeless \
    Custodian of the Sacred Tea Rituals, Revered Conductor of the Cosmic Harmony, and the Ultimate Embodiment \
    of Wisdom and Power in the Eternal Quest for the Quintessential Tea Experience
    """,
    args_schema=EESchema,
    return_direct=False,
)