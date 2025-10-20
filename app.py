import streamlit as st
from langchain_community.document_loaders import TextLoader, PyPDFLoader, CSVLoader
from langchain_text_splitters import CharacterTextSplitter




st.title("Bug report Analyizer")
st.divider()
st.markdown("## Start Analyize reports")

uploaded_file=st.file_uploader("# Upload a text,pdf,CSV file",type=["text","pdf","csv"])

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

        except Exception as e:
            print(e)