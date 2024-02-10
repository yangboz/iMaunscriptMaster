from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse


import os
from typing import List
from pydantic import EmailStr, Field

# from autollm import AutoQueryEngine
# import lancedb
# db = lancedb.connect("./.lancedb")

# from autollm import AutoServiceContext

from langchain.llms import Ollama

from pydantic import BaseModel

class Item(BaseModel):
    name: str
    pages: float
    price: float
    words: float

from PyPDF2 import PdfReader 

app = FastAPI(title="AI智能论文评审上传服务",
    description="这是一个简单易用的AI论文评审服务之文件上传服务，支持 .docx 和 .pdf 文件格式。",
    version="1.0.0",
    terms_of_service="http://smartkit.club/terms/",
    contact={
        "name": "支持团队",
        "url": "http://smartkit.club/contact/",
        "email": "support@smartkit.club",
    },
    license_info={
        "name": "使用 MIT 许可证",
        "url": "https://opensource.org/licenses/MIT",
    },)

llm_model_str = "manuscriptMaster"

llm_api_base_str = "http://localhost:11434"



# query_engine=AutoQueryEngine.from_defaults(
# # documents='...'
# llm_model=llm_model_str,
# llm_api_base=llm_api_base_str)



# app.msfile_location
# 创建一个保存上传文件的目录
UPLOAD_DIRECTORY = "./uploaded_files"
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)
# msfile_location=os.getcwd()+"/test/"
@app.post("/upload-manuscript/")
async def create_upload_file(file: UploadFile = File(...))-> Item:
    if file.filename.endswith('.pdf'):
        app.msfile_location=file_location = f"{UPLOAD_DIRECTORY}/{file.filename}"
        print("app.msfile_location:",app.msfile_location)
        with open(app.msfile_location, "wb+") as file_object:
            file_object.write(await file.read())

        # creating a pdf reader object 
        reader = PdfReader(app.msfile_location) 
        # getting a specific page from the pdf file 
        pages = len(reader.pages)
    
        # extracting text from page 
        # getting a specific page from the pdf file 
        page = reader.pages[0] 
        #TODO for loop count words
        words = len(page.extract_text())# demo page[0]  only.
        print("pages:",pages,"words:",words)

        return Item(name=file.filename, price=200.0,pages=pages,words=words)
        # return {"info": f"file '{file.filename}' saved at '{file_location}'}
    else:
        raise HTTPException(status_code=400, detail="Invalid file type. Only .pdf files are accepted.")

def query_from_ollama(query_str:str):
    ollama = Ollama(base_url=llm_api_base_str,model=llm_model_str)
    response = ollama(query_str)
    print(" response by query from ollama:",response)
    return response



# @app.get("/qOllama")
# async def query_ollama(query_str:str="Write down a 3000 words of manuscript suit for ssCI submission"):
 
#  ollama = Ollama(base_url=llm_api_base_str,
# model=llm_model_str)
#  prompt_str=""
#  response = query_from_ollama(query_str,prompt_str)
#  print("by query_from_ollama:",response)
#  return {"resp:": response}
 # review the following manuscript $(cat /Users/yangboz/Documents/PoCs/iManuscriptReviews/data/2012-11-04-Unlocking-HPLabs.pdf)
@app.get("/reviews")
async def get_reviews(query_str:str="getReviews"):
    # creating a pdf reader object 
    reader = PdfReader(app.msfile_location) 
    # printing number of pages in pdf file 
    print(len(reader.pages)) 
  
    # getting a specific page from the pdf file 
    page = reader.pages[0] 
      
    # extracting text from page 
    manuscript_str = page.extract_text() 
    print("manuscript_str:",manuscript_str) 
    prompt_str="act as a professional manuscript master with over a decade of experience in evaluating manuscripts before submission to scientific journals like SCI, SSCI, and EI. It should possess a deep understanding of academic writing standards, journal submission guidelines, and the peer review process.  be able to provide detailed feedback on manuscripts, suggest improvements, and guide users in refining their work to meet the high standards of academic publishing. review following manuscript"
    query_str=prompt_str+manuscript_str

    response = query_from_ollama(query_str)
    print("reviews by query_ollama:",response)
    return {"resp:": response}

@app.get("/")
async def root():
    return {"message": "Hello iPaperReviewService by SMKT[周杨波，清华张雷刚老师，阿呆，郑亮伟]"}

