import validators, streamlit as st
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_classic.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import YoutubeLoader,UnstructuredURLLoader
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

## streamlit app
st.set_page_config(page_title="LangChain: Summarize Text From YouTube or Website Using Hugging Face", page_icon="🦜")
st.title("🦜 LangChain: Summarize Text From YouTube or Website Using Hugging Face")
st.subheader('Summarize URL')

## Get the Hugging Face API Key and url(YT or website)to be s   ummarized
with st.sidebar:
    hf_api_key=st.text_input("Hugging Face API Token",value="",type="password")

# if not hf_api_key.strip():
#         st.info("Please add the hugging face api key")
#         st.stop()

generic_url=st.text_input("URL",label_visibility="collapsed")

## Gemma Model USsing Hugging Face API

prompt_template="""
Provide a summary of the following content under 500 words:
Content:{text}

"""
prompt=PromptTemplate(template=prompt_template,input_variables=["text"])

if st.button("Summarize"):
    ## Validate all the inputs
    if not hf_api_key.strip() or not generic_url.strip():
        st.error("Please provide the information to get started")
    elif not validators.url(generic_url):
        st.error("Please enter a valid Url. It can may be a YouTube video url or website url")
    else:
        try:
            llm = HuggingFaceEndpoint(
                repo_id="google/gemma-4-31B-it", 
                huggingfacehub_api_token=hf_api_key.strip(), 
                streaming=True, 
                max_new_tokens=200, 
                temperature=0.5
            )
            chat_model = ChatHuggingFace(llm=llm)
            with st.spinner("Waiting..."):
                ## loading the website or youtube video data
                if "youtube.com" in generic_url or "youtu.be" in generic_url:
                    loader=YoutubeLoader.from_youtube_url(generic_url)
                else:
                    loader=UnstructuredURLLoader(urls=[generic_url],ssl_verify=False,
                                                 headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"})
                docs=loader.load()

                ## Chain For Summarization
                chain=load_summarize_chain(chat_model,chain_type="stuff",prompt=prompt)
                output_summary=chain.invoke({"input_documents": docs})
                
                st.success(output_summary["output_text"])
        except Exception as e:
            st.exception(e)
                    
