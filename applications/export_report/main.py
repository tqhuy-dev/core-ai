import gradio as gr
import os
import pandas as pd
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.tools import create_retriever_tool
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from applications.export_report.graph import init_graph_agent

map_file_name = {}
global graph_agent

def load_into_pandas(file):
    """
    Load data from an Excel file into a pandas DataFrame.

    Args:
        file: Path to the Excel file

    Returns:
        pandas.DataFrame: DataFrame containing the Excel data
    """
    return pd.read_excel(file)

def save_into_vector_store(df, file_name):
    """
    Save data from a pandas DataFrame into a vector store.
    """
    chunks = []
    for idx, row in df.iterrows():
        row_text = ", ".join([f"{col}: {row[col]}" for col in df.columns])
        chunks.append(row_text)

    docs = [Document(page_content=chunk) for chunk in chunks]
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents(docs)
    embeddings = OpenAIEmbeddings()
    vs_name = f"vs_{file_name}"
    if os.path.exists(vs_name):
        Chroma(persist_directory=vs_name, embedding_function=embeddings).delete_collection()
    vectorstore = Chroma.from_documents(documents=split_docs,
                                        embedding=embeddings,
                                        persist_directory=vs_name)
    return vectorstore



def process_file(file_obj):
    """
    Process the uploaded file and return a message.
    This function is called when a file is uploaded.
    """
    if file_obj is None:
        return None, gr.update(visible=False), gr.update(visible=False)

    # Get the file name
    file_name = os.path.basename(file_obj.name)

    # Here you would typically process the file
    # For demonstration, we'll just return the file name

    # Example of using the load_into_pandas function
    df = load_into_pandas(file_obj.name)
    vectorstore = save_into_vector_store(df, file_name)
    retriever = vectorstore.as_retriever()
    retriever_tool = create_retriever_tool(retriever, 
                                           f"search_internal_documents_of_data",
                                           f"Search internal documents of data")
    map_file_name[file_name] = retriever_tool
    global graph_agent
    graph_agent = init_graph_agent(retriever_tool)
    # Make the text input visible and hide the file input
    return f"File '{file_name}' uploaded successfully. Please enter your text:", gr.update(visible=True), gr.update(visible=False)

def process_text(text):
    """
    Process the entered text.
    This function is called when text is submitted.
    """
    if not text:
        return "No text entered."

    # Here you would typically process the text
    # For demonstration, we'll just return the text
    global graph_agent
    response = graph_agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": f"{text}",
            }
        ]
    })
    text = response["messages"][-1].content
    return f"You entered: {text}"

def reset_interface():
    """
    Reset the interface to its initial state.
    """
    map_file_name.clear()
    global graph_agent
    graph_agent = None
    return None, gr.update(value="", visible=False), gr.update(visible=True)

# Create the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# Dynamic Form Application")

    # Output area for messages
    output_message = gr.Markdown()

    # Text input (initially hidden)
    text_input = gr.Textbox(
        label="Enter your text",
        placeholder="Type here...",
        visible=False
    )

    # File input (initially visible)
    file_input = gr.File(
        label="Upload a file",
        file_types=[".xlsx"]
    )

    # Submit buttons
    with gr.Row():
        file_submit = gr.Button("Submit File")
        text_submit = gr.Button("Submit Text", visible=False)
        reset_button = gr.Button("Reset")

    # Set up event handlers
    file_submit.click(
        fn=process_file,
        inputs=[file_input],
        outputs=[output_message, text_input, file_input]
    ).then(
        fn=lambda: gr.update(visible=True),
        outputs=[text_submit]
    )

    text_submit.click(
        fn=process_text,
        inputs=[text_input],
        outputs=[output_message]
    )

    reset_button.click(
        fn=reset_interface,
        outputs=[output_message, text_input, file_input]
    ).then(
        fn=lambda: [gr.update(visible=False), gr.update(visible=True)],
        outputs=[text_submit, file_submit]
    )

# Launch the app
if __name__ == "__main__":
    demo.launch()
