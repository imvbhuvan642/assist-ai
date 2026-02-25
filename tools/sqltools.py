import os
from dotenv import load_dotenv
load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase

model_gemini = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=1)

db_url = os.getenv("DATABASE_URL")
print(db_url)
db = SQLDatabase.from_uri(db_url, sample_rows_in_table_info=3)

# Create SQL toolkit and get tools
toolkit = SQLDatabaseToolkit(db=db, llm=model_gemini)
sql_tools = toolkit.get_tools()