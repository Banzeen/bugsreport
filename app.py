import streamlit as st
from langchain_community.document_loaders import TextLoader, PyPDFLoader, CSVLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

st.title("Bug report Analyizer")
st.divider()
st.markdown("## Start Analyize reports")

uploaded_file=st.file_uploader("# Upload a text,pdf,CSV file",type=["txt","pdf","csv"])

llm = ChatOpenAI(model="gpt-4o-mini")

parser = StrOutputParser()

prompt_template = ChatPromptTemplate.from_template("Summarize the following document {document}")


chain = prompt_template | llm | parser


if uploaded_file is not None:
    with st.spinner("Processing..."):
        try:
            print("File: ", uploaded_file)
            print("File Type: ", uploaded_file.type)
            
            temp_file_path = uploaded_file.name
            print("File path: ", temp_file_path)
            
            # Save uploaded file
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            # Create document loader
            if uploaded_file.type == "text/plain":
                loader = TextLoader(temp_file_path)
            elif uploaded_file.type == "text/csv":
                loader = CSVLoader(temp_file_path)
            elif uploaded_file.type == "application/pdf":
                loader = PyPDFLoader(temp_file_path)
            else:   
                st.error("File type is not supported!")
                st.stop()

            #creat doc
            doc = loader.load()
            print(doc)

            text_splitter=CharacterTextSplitter(chunk_size=1000,chunk_overlab=100)

            chunks=text_splitter.split_documents(doc)
            print(chunks)

        except Exception as e:
            print(e)

    st.success("File uploaded")

if st.button("Analyize"):
        container = st.empty()
        chunk_summaries = []

        with st.spinner("Analyize report"):
            try:
                for i, chunk in enumerate(chunks):
                    print(f"Processing chunk {i + 1}/{len(chunks)}")
               
               # prompt
                    chunk_prompt = ChatPromptTemplate.from_template(
                   "You are a highly skilled AI model tasked with summarizing text. "
                    "Please summarize the following chunk of text in a concise manner, "
                    "highlighting the most critical information. Do not omit any key details:\n\n{document}"
               ) 
               
               # chain
                    chunk_chain = chunk_prompt | llm | parser
                    chunk_summary = chunk_chain.invoke({"document": chunk})
                    chunk_summaries.append(chunk_summary)
        
            except Exception as e:
                print("Error summarizing chunks", e)
                st.error(f"Error summarizing chunks: {e}")
                st.stop()
