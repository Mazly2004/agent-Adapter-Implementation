from typing import List, TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import WikipediaLoader
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set.")

class GraphState(TypedDict):
    question: str
    retrievedDocs: List[str]
    initialResponse: str
    finalResponse: str
    selfCheckResult: str
    sentiment: str
    messages: List[BaseMessage]

def make_vector_store():

    wiki_loader_global = WikipediaLoader(query="Econet Global", load_max_docs=1)
    wiki_loader_zimbabwe = WikipediaLoader(query="Econet Zimbabwe", load_max_docs=1)

    # Load the Econet website pages using WebBaseLoader
    web_urls = ["https://www.econet.co.zw/usd-data-bundles", "https://www.econet.co.zw/zwg-data-bundles/"]
    web_loader = WebBaseLoader(web_urls)

    # Combine documents from all loaders
    documents = []
    documents.extend(wiki_loader_global.load())
    documents.extend(wiki_loader_zimbabwe.load())
    documents.extend(web_loader.load())
    

    textSplitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splitDocs = textSplitter.split_documents(documents)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=API_KEY)
    persist_directory = "./chroma_db"
    vector_store = Chroma.from_documents(splitDocs, embeddings, persist_directory=persist_directory)
    return vector_store

library = make_vector_store()
retriever = library.as_retriever()
contextualizePrompt = ChatPromptTemplate.from_messages([
    ("system", "Given the conversation history and a user's question, generate a standalone question that can be used for RAG."),
    MessagesPlaceholder("chat_history"),
    ("user", "{input}"),
])
historyAwareRetriever = create_history_aware_retriever(
    llm=ChatGoogleGenerativeAI(model="gemini-2.5-pro"),
    retriever=retriever,
    prompt=contextualizePrompt
)

def initialize_state(state: GraphState):
    question = state["question"]
    messages = [HumanMessage(content=question)]
    return {"messages": messages}

def retrieveDocuments(state: GraphState):
    question = state["question"]
    messages = state["messages"]
    retrieved_docs = []
    try:
        retrieved_docs_output = historyAwareRetriever.invoke({"input": question, "chat_history": messages})
        if isinstance(retrieved_docs_output, list) and all(isinstance(doc, Document) for doc in retrieved_docs_output):
            retrieved_docs = retrieved_docs_output
    except Exception as e:
        pass
    return {"retrievedDocs": retrieved_docs}

llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", google_api_key=API_KEY)
ragPrompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful chatbot for a company. Answer the user's question truthfully based only on the provided context. If you don't know the answer, politely state that you can't find the information. Context: {context}"),
    ("user", "{question}"),
])
ragChain = ragPrompt | llm | StrOutputParser()

def initialResponse(state: GraphState) -> GraphState:
    retrievedDocs = state["retrievedDocs"]
    question = state["question"]
    if not retrievedDocs:
        return {"initialResponse": "No relevant documents found."}
    context = "\n\n".join(doc.page_content for doc in retrievedDocs)
    response = ragChain.invoke({"context": context, "question": question})
    return {"initialResponse": response}

selfCheckPrompt = PromptTemplate(
    template="""
    You are a quality assurance agent for a customer service chatbot. Your task is to review a generated response and determine if it is accurate and appropriate.

    User Question: {question}
    Retrieved Context: {retrievedDocs}
    Initial Response: {initialResponse}

    Critique the Initial Response. Consider the following:
    1. Does the response directly and accurately answer the question?
    2. Does it use ONLY the information from the provided context?
    3. Is the tone helpful and appropriate?
    4. Does it contain any hallucinations or irrelevant information?

    Based on your critique, classify the response. Respond with either 'Correct' if it is good to go, or 'Incorrect' if it needs a rewrite.""",
    input_variables=["question", "retrievedDocs", "initialResponse"]
)
selfCheckChain = selfCheckPrompt | llm | StrOutputParser()

def selfCheck(state: GraphState) -> GraphState:
    question = state["question"]
    retrievedDocs = state["retrievedDocs"]
    initial_response = state["initialResponse"]
    if not retrievedDocs:
        return {"selfCheckResult": "No relevant documents found."}
    context = "\n\n".join(doc.page_content for doc in retrievedDocs)
    result = selfCheckChain.invoke({
        "question": question,
        "retrievedDocs": context,
        "initialResponse": initial_response
    })
    return {"selfCheckResult": result}

def sentimentAnalysis(state: GraphState) -> GraphState:
    question = state["question"]
    sentimentPrompt = PromptTemplate(
        template="Analyze the sentiment of the following user query and classify it as 'positive', 'negative', or 'neutral'.\nQuery: {question}",
        input_variables=["question"]
    )
    sentimentChain = sentimentPrompt | llm | StrOutputParser()
    sentiment = sentimentChain.invoke({"question": question})
    return {"sentiment": sentiment.strip().lower()}

rewritePrompt = PromptTemplate(
    template="""
    The previous response was deemed 'Incorrect' for the following reasons: {self_check_result}.

    User Question: {question}
    Retrieved Context: {retrieved_docs}

    Rewrite a new, accurate, and helpful response based on the feedback and the provided context.
    """,
    input_variables=["question", "retrieved_docs", "self_check_result"]
)
rewriteChain = rewritePrompt | llm | StrOutputParser()

def rewrittenResponseNode(state: GraphState) -> GraphState:
    question = state["question"]
    retrievedDocs = state["retrievedDocs"]
    selfCheckResult = state["selfCheckResult"]
    if not retrievedDocs:
        return {"final_response": "No relevant documents found."}
    context = "\n\n".join(doc.page_content for doc in retrievedDocs)
    rewrittenResponse = rewriteChain.invoke({
        "question": question,
        "retrieved_docs": context,
        "self_check_result": selfCheckResult
    })
    return {"finalResponse": rewrittenResponse}

workflow = StateGraph(GraphState)
workflow.add_node("initialize_state", initialize_state)
workflow.add_node("analyze_sentiment", sentimentAnalysis)
workflow.add_node("retrieve_docs", retrieveDocuments)
workflow.add_node("generate_response", initialResponse)
workflow.add_node("self_check_response", selfCheck)
workflow.add_node("rewrite_response", rewrittenResponseNode)

def route_check_result(state: GraphState):
    if state["selfCheckResult"] == "Correct":
        return "end_with_initial"
    else:
        return "rewrite"

workflow.set_entry_point("initialize_state")
workflow.add_edge("initialize_state", "analyze_sentiment")
workflow.add_edge("analyze_sentiment", "retrieve_docs")
workflow.add_edge("retrieve_docs", "generate_response")
workflow.add_edge("generate_response", "self_check_response")
workflow.add_conditional_edges(
    "self_check_response",
    route_check_result,
    {
        "end_with_initial": END,
        "rewrite": "rewrite_response"
    }
)
workflow.add_edge("rewrite_response", END)
app = workflow.compile()