# THIS FILE OUTLINES HOW I HAVE ACCOMPLISHED THE INFORMED CONSENT PROBLEM
# IN AN OLD NOTEBOOK PROTOTYPE WITHOUT A FRONT END.
# THIS FILE IS FOR REVIEW ONLY AND SHOULD NOT BE EXECUTED DIRECTLY.

#ALL THE IMPORTS THAT I NEEDED 
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents.base import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken
import getVectorstore                               #This was a file that created a qdrant vectorstore
from getVectorstore import getVectorstore
from qdrant_client.http import models as rest
from dotenv import load_dotenv
import os, getpass, time
import prompts                                      #prompts was just a file containing a rag prompt template
from prompts import rag_prompt_template
from langchain.prompts import ChatPromptTemplate
from defaults import default_llm
from operator import itemgetter
from langchain.schema.output_parser import StrOutputParser
from datetime import date
import queries
from queries import summary_query                   #queries was just a file containing exportable user queries for each section
from queries import background_query
from queries import number_of_participants_query
from queries import study_procedures_query
from queries import alt_procedures_query
from queries import risks_query
from queries import benefits_query
import makeMarkdown
from makeMarkdown import makeMarkdown
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from IPython.display import Image, display
from langchain_core.messages import HumanMessage

# Load the document - here we are just using a protocol in a specific directory
# In the demo project this will come from Jeeva's code
file_path = './documents/protocol.pdf'
# file_path = './documents/consent.pdf'
separate_pages = []             
loader = PyMuPDFLoader(file_path)
page = loader.load()
separate_pages.extend(page)
print(f"Number of separate pages: {len(separate_pages)}")

# OyMuPDFLoader loads pages into separate docs!
# This is a problem when we chunk because we only chunk individual
# documents.  We need ONE overall document so that the chunks can
# overlap between actual PDF pages.
document_string = ""
for page in separate_pages:
    document_string += page.page_content
print(f"Length of the document string: {len(document_string)}")

# CHOP IT UP
def tiktoken_len(text):
    tokens = tiktoken.encoding_for_model("gpt-4o").encode(
        text,
    )
    return len(tokens)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap = 200,
    length_function = tiktoken_len
)
text_chunks = text_splitter.split_text(document_string)
print(f"Number of chunks: {len(text_chunks)} ")
document = [Document(page_content=chunk) for chunk in text_chunks]
print(f"Length of  document: {len(document)}")

qdrant_vectorstore = getVectorstore(document, file_path)

# Helper function that lets me create a retriever for a specific document
"""
This code sets up the search type but more importantly it has the filter
set up correctly.  We get a list of document titles that we want to include
in the filter, and pass it into the function, returning the retriever.

"""

def create_protocol_retriever(document_titles):
    return qdrant_vectorstore.as_retriever(
        search_kwargs={
            'filter': rest.Filter(
                must=[
                    rest.FieldCondition(
                        key="metadata.document_title",
                        match=rest.MatchAny(any=document_titles)
                    )
                ]
            ),
            'k': 15,                                       
        }
    )

# Usage example
# document_titles = ["consent.pdf", "protocol.pdf"]
document_titles = ["protocol.pdf"]
protocol_retriever = create_protocol_retriever(document_titles)

# Create prompt
rag_prompt = ChatPromptTemplate.from_template(prompts.rag_prompt_template)

llm = default_llm

rag_chain = (
    {"context": itemgetter("question") | protocol_retriever, "question": itemgetter("question")}
    | rag_prompt | llm | StrOutputParser()
)

# NOTE THE STRUCTURE OF THIS RAG CHAIN AS I LATER USE IT IN THE AGENDS.

# HERE IS HOW I CREATED THE AGENTS AND TRACKED THE STATE

# Create AgentState object and include all the pieces in separate fields
# Not sure if add_messages is necessary because I don't have any overwrites later (YET)
# But future enhancement might include a subnetwork that edits each piece further
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]     # not sure I need this
    summary: Annotated[str, add_messages]
    background: Annotated[str, add_messages]
    number_of_participants: Annotated[str, add_messages]
    study_procedures: Annotated[str, add_messages]
    alt_procedures: Annotated[str, add_messages]
    risks: Annotated[str, add_messages]
    benefits: Annotated[str, add_messages]


# Set up all the node definitions - each simply returns its query
def summary_node(state):
    summary = rag_chain.invoke({"question":summary_query()})
    return {"summary":[summary]}

def background_node(state):
    background = rag_chain.invoke({"question":background_query()})
    return {"background":[background]}

def number_of_participants_node(state):
    number_of_participants = rag_chain.invoke({"question":number_of_participants_query()})
    return {"number_of_participants": [number_of_participants]}

def study_procedures_node(state):
    study_procedures = rag_chain.invoke({"question":study_procedures_query()})
    return {"study_procedures": [study_procedures]}

def alt_procedures_node(state):
    alt_procedures = rag_chain.invoke({"question":alt_procedures_query()})
    return {"alt_procedures": [alt_procedures]}

def risks_node(state):
    risks = rag_chain.invoke({"question":risks_query()})
    return {"risks": [risks]}

def benefits_node(state):
    benefits = rag_chain.invoke({"question":benefits_query()})
    return {"benefits": [benefits]}

# Now construct the graph.  My first attempt simply linked them in
# sequence to mimic the brute force method done earlier.  But this
# graph runs the agents in parallel.

uncompiled_graph = StateGraph(AgentState)

# Add nodes
uncompiled_graph.add_node("Summarizer", summary_node)
uncompiled_graph.add_node("Background", background_node)
uncompiled_graph.add_node("Numbers", number_of_participants_node)
uncompiled_graph.add_node("Procedures", study_procedures_node)
uncompiled_graph.add_node("Alternatives", alt_procedures_node)
uncompiled_graph.add_node("Risks", risks_node)
uncompiled_graph.add_node("Benefits", benefits_node)

# Edges from the START
uncompiled_graph.add_edge(START,"Summarizer")
uncompiled_graph.add_edge(START,"Background")
uncompiled_graph.add_edge(START,"Numbers")
uncompiled_graph.add_edge(START,"Procedures")
uncompiled_graph.add_edge(START,"Alternatives")
uncompiled_graph.add_edge(START,"Risks")
uncompiled_graph.add_edge(START,"Benefits")

# Edges to the END
uncompiled_graph.add_edge("Summarizer",END)
uncompiled_graph.add_edge("Background",END)
uncompiled_graph.add_edge("Numbers",END)
uncompiled_graph.add_edge("Procedures",END)
uncompiled_graph.add_edge("Alternatives",END)
uncompiled_graph.add_edge("Risks",END)
uncompiled_graph.add_edge("Benefits",END)

compiled_graph = uncompiled_graph.compile()

start_time = time.time()
inputs = {"messages":[HumanMessage(content="")]}
result = compiled_graph.invoke(inputs)
end_time = time.time()
execution_time = end_time - start_time
print(f"Agent based (parallel) execution time: {execution_time:.2f} seconds.")

pieces_of_consent = [
    result['summary'][-1].content,
    result['background'][-1].content,
    result['number_of_participants'][-1].content,
    result['study_procedures'][-1].content,
    result['alt_procedures'][-1].content,
    result['risks'][-1].content,
    result['benefits'][-1].content,
]
ICF_title = "Agent Written ICF"
makeMarkdown(pieces_of_consent, ICF_title)  #This function just glued the document today and made Markdown
print("Done")