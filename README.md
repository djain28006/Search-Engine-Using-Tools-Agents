# 🔎 AI Search Agent: A Multi-Tool Research Assistant

A high-performance intelligent agent built with **LangChain** and **Streamlit** that acts as a specialized search engine. Unlike standard LLMs that rely solely on training data, this agent uses **Retrieval-Augmented Generation (RAG)** and **Tool-Calling** to provide fact-grounded answers from live sources.

🚀 **[View Live Demo](https://search-engine-using-tools-agents-n3matyv6frxjtmxdjctzwh.streamlit.app/)**

---

## 🖼️ Preview
![AI Search Agent Interface](.png)

---

## 🌟 Key Features

* **Dynamic Decision Making**: Uses an OpenAI Functions Agent to decide which tool is best suited for your specific query.
* **Three-Pillar Knowledge Base**:
    * **Wikipedia**: For general facts, history, and broad context.
    * **Arxiv**: Fetches the latest research papers and scientific abstracts.
    * **LangChain Docs**: A custom RAG pipeline that searches official documentation via a FAISS vector database.
* **Execution Transparency**: Features a "Tool Execution" section that shows the raw data the agent found before synthesizing the final answer.
* **Performance Optimized**: Utilizes Streamlit caching (`@st.cache_resource`) to ensure the vector database is built only once.

---

## 🛠️ Tech Stack

* **Core Framework**: LangChain (Agents, Tools, Retrievers)
* **Frontend**: Streamlit
* **LLM**: GPT-4o-mini
* **Vector Store**: FAISS
* **Embeddings**: OpenAI Embeddings

---

## 🚀 Installation & Local Deployment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/djain28006/search-engine-using-tools-agents.git
   cd search-engine-using-tools-agents
