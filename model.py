import os
from langchain.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEndpoint
from langchain.chains import RetrievalQA
import chainlit as cl
import logging
logging.basicConfig(level=logging.DEBUG)

DB_FAISS_PATH = 'vectorstore/db_faiss'

custom_prompt_template = """
You are an Ayurveda Advisor. Use the following pieces of information to answer the user's question in detail. When discussing 
medicines and remedies, ensure to include precautions and exceptions where necessary. Don't include references section.
Create a stand-alone question from follow-up questions while retaining context from the previous exchanges.
Format the entire answer in markdown format, with bolds, italics, and pointers wherever required.
Only return the helpful answer below and nothing else. For answers exceeding 120 tokens, answer in points.
Context: {context}
Question: {question}
"""

def set_custom_prompt():
    prompt = PromptTemplate(template=custom_prompt_template, input_variables=["context", "question"])
    return prompt


class Document:
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata

def add_sources_to_answer(sources, answer):
    if(len(sources) > 0):
        answer += f"\n#### References\n"
        i = 0
        for source in sources:
            i += 1
            answer += format_source_content(source, i)
    return answer

def format_source_content(source, i):
    metadata = source.metadata
    file_name = metadata["source"].split('\\')[-1].split(".pdf")[0]
    page_content = source.page_content
    formatted_content = f"##### {i}.{file_name}\n"
    formatted_content += f"Source Content: _{page_content}_\n"
    return formatted_content


def retrieval_qa_chain(llm, prompt, db):
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=db.as_retriever(search_kwargs={"k": 2}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )
    return qa_chain

def handle_query(question):
    qa_result = create_chat_bot_chain()
    response = qa_result({'query': question})
    return response

def load_llm():
    llm = HuggingFaceEndpoint(
        repo_id="mistralai/Mistral-7B-Instruct-v0.2", 
        huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_ACESS_TOKEN"), 
        max_new_tokens=1024,
        temperature=0.1,
        model_kwargs={"max_length": 64} 
    )
    return llm

def create_chat_bot_chain():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2",
                                       model_kwargs={'device': 'cpu'})
    db = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)    
    llm = load_llm()
    qa_prompt = set_custom_prompt()
    qa_chain = retrieval_qa_chain(llm, qa_prompt, db)
    return qa_chain

@cl.on_chat_start
async def on_chat_start():
    chain = create_chat_bot_chain()
    msg = cl.Message(content="Starting the Bot .............")
    await msg.send()
    msg.content = "Hi, How Are You ?? Welcome to Vedabot. What is your problem?"
    await msg.update()
    cl.user_session.set("context", [])
    cl.user_session.set("chain", chain) 

@cl.on_message
async def on_message(message: cl.Message):
    print("User: " + message.content)
    chain = cl.user_session.get("chain")
    message_history = cl.user_session.get("context")
    message_history.append({"role": "user", "content": message.content})
    cl.user_session.set("context", message_history)
    
    cb = cl.AsyncLangchainCallbackHandler(
        stream_final_answer=True, answer_prefix_tokens=["FINAL", "ANSWER"]
    )
    cb.answer_reached = True

    # Include all messages in the combined input
    combined_input = " ".join([m['content'] for m in message_history])
    
    res = await chain.ainvoke(combined_input, callbacks=[cb])
    answer = res["result"]
    print(answer)
    sources = res["source_documents"]
    answer = add_sources_to_answer(sources, answer)
    message_history.append({"role": "assistant", "content": answer})

    cl.user_session.set("context", message_history)
    await cl.Message(content=answer).send()
