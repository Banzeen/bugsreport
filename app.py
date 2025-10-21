import streamlit as st
from langchain_community.document_loaders import TextLoader, PyPDFLoader, CSVLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os


load_dotenv()


st.set_page_config(page_title="Bug Report Analyzer", page_icon="🛡️", layout="wide")

st.title("🛡️ Bug Report Analyzer")
st.divider()
st.markdown("## Upload and Analyze Security Reports using AI")


uploaded_file = st.file_uploader(
    "### 📤 Upload a TXT, PDF, or CSV file", 
    type=["txt", "pdf", "csv"]
)


llm = ChatOpenAI(model="gpt-4o-mini")
parser = StrOutputParser()


if uploaded_file is not None:
    with st.spinner(" Processing file..."):
        try:
            temp_file_path = uploaded_file.name

       
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

   
            if uploaded_file.type == "text/plain":
                loader = TextLoader(temp_file_path)
            elif uploaded_file.type == "text/csv":
                loader = CSVLoader(temp_file_path)
            elif uploaded_file.type == "application/pdf":
                loader = PyPDFLoader(temp_file_path)
            else:
                st.error(" Unsupported file type!")
                st.stop()

        
            doc = loader.load()

         
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = text_splitter.split_documents(doc)

        
            st.session_state["chunks"] = chunks

            st.success(f" File uploaded successfully and divided into {len(chunks)} chunks.")

        except Exception as e:
            st.error(f"Error loading file: {e}")
            st.stop()


if st.button("🔍 Analyze"):
    if "chunks" not in st.session_state:
        st.error(" Please upload and process a file first.")
        st.stop()

    chunks = st.session_state["chunks"]
    container = st.empty()
    chunk_summaries = []

 
    with st.spinner(" Analyzing report chunks..."):
        try:
            for i, chunk in enumerate(chunks):
                st.write(f"Processing chunk {i+1}/{len(chunks)}...")

                chunk_prompt = ChatPromptTemplate.from_template("""
You are a highly skilled **Cybersecurity AI Analyst** specialized in vulnerability triage and technical threat analysis.

Your task is to analyze the following section of a bug report and provide a structured summary with:
1️⃣ **Vulnerability Type** — classify it precisely (e.g., SQL Injection, XSS, CSRF, Privilege Escalation, etc.)
2️⃣ **Root Cause** — explain *why* it happens (e.g., unsanitized input, insecure API endpoint, etc.)
3️⃣ **Impact Severity** — rate the impact (Low / Medium / High / Critical)
4️⃣ **Exploitation Feasibility** — how likely it is to be exploited
5️⃣ **Recommended Fix** — suggest a concise mitigation or patch strategy
6️⃣ **Summary** — a short technical recap (1–2 sentences)

Analyze the following report section carefully and extract insights accordingly:

{document}
""")

                chunk_chain = chunk_prompt | llm | parser
                chunk_summary = chunk_chain.invoke({"document": chunk.page_content})
                chunk_summaries.append(chunk_summary)

        except Exception as e:
            st.error(f" Error summarizing chunks: {e}")
            st.stop()

    
    with st.spinner(" Creating final summary..."):
        try:
            combined_summaries = "\n".join(chunk_summaries)

            final_prompt = ChatPromptTemplate.from_template("""
You are a **Senior Security Engineer** preparing a consolidated professional report
based on multiple vulnerability summaries analyzed by junior analysts.

Your goal is to merge and refine the following summaries into a single, coherent report
with the following structured sections:

---
### 🧩 Vulnerability Overview
Summarize all unique vulnerabilities mentioned and categorize them (e.g., Injection, Access Control, Logic Flaw).

### 🔍 Root Cause Analysis
Describe the common technical reasons behind these vulnerabilities and any patterns observed.

### ⚠️ Severity Assessment
Provide an overall severity rating (Low / Medium / High / Critical) for the entire report,
justifying your reasoning.

### 🧠 Exploitation Scenarios
Briefly explain how an attacker might exploit the identified vulnerabilities.

### 🛡️ Remediation Recommendations
Provide actionable recommendations for developers or security engineers to fix the issues and prevent recurrence.

### 📄 Executive Summary
Write a concise summary paragraph suitable for a management-level audience.

---

Here are the summarized chunks you should combine:
{document}
""")

            final_chain = final_prompt | llm | parser
            final_summary = final_chain.invoke({"document": combined_summaries})

          
            st.subheader("🧾 Final Consolidated Security Report")
            container.write(final_summary)

        

            st.success(" Analysis completed successfully!")

        except Exception as e:
            st.error(f" Error creating final summary: {e}")
