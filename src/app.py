import streamlit as st
from MangaDownloader import downloadManga,setup_logger


st.title("Manga Manager")

url = st.text_input('put the manga URL here')
name = st.text_input('put manga name')
button = st.button("Generate")

# if(url and name):
#     log_file = f"thread_MAIN.log"
#     logger = setup_logger(f"thread_MAIN.log", log_file)
#     downloadManga(mangaName=name,url = url,startChapterNo=0,endChapterNo=5,logger = logger)

if(button):
    if(url and name):
        log_file = f"thread_MAIN.log"
        logger = setup_logger(f"thread_MAIN.log", log_file)
        downloadManga(mangaName=name,url = url,startChapterNo=0,endChapterNo=5,logger = logger)

print("hello")