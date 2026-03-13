import os
import streamlit as st
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_core.tools import tool
from langchain.agents import create_agent
from langsmith import Client

# ---------------------------------
# Load environment variables
# ---------------------------------
load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Search_Engine_Tool_Agents"

# ---------------------------------
# Streamlit UI
# ---------------------------------
st.set_page_config(page_title="AI Search Agent", page_icon="🔎")

st.title("🔎 AI Search Agent")
st.write(
    """
Ask any question. The agent can search from:
- Wikipedia
- Arxiv research papers
- LangChain documentation
"""
)

# Sidebar API Key
openai_api_key = st.sidebar.text_input(
    "Enter your OpenAI API key",
    type="password"
)

if not openai_api_key:
    st.info("Please enter your OpenAI API key to continue.")
    st.stop()

os.environ["OPENAI_API_KEY"] = openai_api_key

# ---------------------------------
# Tools
# ---------------------------------
# Wikipedia tool
wiki_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=500)
wiki = WikipediaQueryRun(api_wrapper=wiki_wrapper)

# Arxiv tool
arxiv_wrapper = ArxivAPIWrapper(top_k_results=5, doc_content_chars_max=2000)
arxiv = ArxivQueryRun(api_wrapper=arxiv_wrapper)

# ---------------------------------
# Build Vector Database (cached)
# ---------------------------------
@st.cache_resource
def build_vector_db():
    loader = WebBaseLoader("https://docs.langchain.com/")
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    documents = splitter.split_documents(docs)

    vectordb = FAISS.from_documents(
        documents,
        OpenAIEmbeddings()
    )
    return vectordb

vectordb = build_vector_db()
retriever = vectordb.as_retriever()

# ---------------------------------
# Custom tool for LangChain docs
# ---------------------------------
@tool
def langchain_docs_search(query: str) -> str:
    """Search information about LangChain or LangSmith."""
    docs = retriever.invoke(query)
    return "\n\n".join([doc.page_content for doc in docs])

tools = [wiki, arxiv, langchain_docs_search]

# ---------------------------------
# LLM
# ---------------------------------
llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=openai_api_key
)

# ---------------------------------
# Few-shot Prompt for Agent
# ---------------------------------
client = Client()

few_shot_prompt = """
You are an AI assistant with access to three tools:

- Wikipedia: for general knowledge
- Arxiv: for research papers
- LangChain Docs: for framework-specific questions

Example 1:
User: What is LangChain?
Tool Used: LangChain Docs
Answer: LangChain is a framework for building applications using large language models. Refer to LangChain Docs for details.

Example 2:
User: Who won the Nobel Prize in Physics in 2022?
Tool Used: Wikipedia
Answer: The 2022 Nobel Prize in Physics was awarded to Alain Aspect, John F. Clauser, and Anton Zeilinger.

Example 3:
User: Show me recent papers about transformers.
Tool Used: Arxiv
Answer: You can find the latest papers on transformers on Arxiv. Here are the top results...

Now answer the following question:
"""

# Combine few-shot examples with original system prompt
system_prompt = few_shot_prompt + "\n" + client.pull_prompt("hwchase17/openai-functions-agent").messages[0].prompt.template

# Create agent with updated system prompt
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt
)

# ---------------------------------
# User Input
# ---------------------------------
user_question = st.text_input("Ask a question")

if user_question:

    st.write("##  Agent Tool Execution")

    response = agent.invoke(
        {"messages": [{"role": "user", "content": user_question}]}
    )

    shown_tools = set()
    final_answer = ""

    # Display tool outputs (without duplicates)
    for msg in response["messages"]:
        if msg.type == "tool" and msg.name not in shown_tools:
            st.subheader(f" Tool Used: {msg.name}")
            st.write(msg.content)
            shown_tools.add(msg.name)
        if msg.type == "ai":
            final_answer = msg.content

    # Final answer
    st.write("##  Final Answer")
    st.success(final_answer)