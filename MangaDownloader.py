# https://www.google.com/about/careers/applications/jobs/results?target_level=EARLY&degree=BACHELORS&location=India


import requests
from bs4 import BeautifulSoup
from PIL import Image
import re
import io
import threading
import time
import logging
import os
import json
import sys


DEFAULT_LOGGER = "defaultLogger"
DEFAUL_LOG_FILE = "default.log"


def setup_logger(name, log_file):
    """Function to set up a logger for a specific thread"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create a file handler
    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setLevel(logging.DEBUG)

    # Create a formatter and set it for the handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(file_handler)
    
    return logger


def replace_numbers(text, replacement=0):
    if not isinstance(text, str):  # Ensure text is a string
        text = str(text)  
    return re.sub(r'\d+', str(replacement), text)


def images_bin_to_pdf(image_paths, output_folder="pdf_output", output_pdf="output.pdf",logger=setup_logger(DEFAULT_LOGGER,DEFAUL_LOG_FILE)):
    try:
        # Open the first image and convert it to RGB (PDF doesn't support RGBA)
        images = [Image.open(io.BytesIO(img)).convert("RGB") for img in image_paths]

        # Create full path for the output PDF
        output_folder = os.path.join("Downloads",output_folder)
        os.makedirs(output_folder, exist_ok=True)
        output_pdf_path = os.path.join(output_folder, output_pdf)
        # output_pdf_path = os.path.join("Downloads", output_pdf_path)
        # Save as PDF
        images[0].save(output_pdf_path, save_all=True, append_images=images[1:])
        logger.info(f"PDF created successfully {output_pdf_path}")
        print(f"PDF created successfully: {output_pdf_path}")
    except Exception as e:
        # pass
        print(f"Error: {e}")


def returnImage(url, filename="downloaded_image.jpg",logger=setup_logger(DEFAULT_LOGGER,DEFAUL_LOG_FILE)):
    try:
        response = requests.get(url, stream=True, verify = False)
        response.raise_for_status()  # Raise error for bad responses (4xx and 5xx)
        return response.content
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading image: {e}")
        print(f"Error downloading image: {e}")
        return False

def scrapSingleChapter(pageUrl,folderName = "",logger=setup_logger(DEFAULT_LOGGER,DEFAUL_LOG_FILE)):
    logger.info(f"requesting the data for page {pageUrl}")
    try:
        response = requests.get(pageUrl,verify = False)
        soup = BeautifulSoup(response.text, "html.parser")

        imgs = soup.find_all('img')
        totalImgs = len(list(imgs))
        imageIndex = 0
        imageBaseName = "image"
        imagesList = []
        for item in imgs:
            imageIndex += 1
            newImageName = imageBaseName + str(imageIndex) + ".jpg"
            logger.info(f"fetching {imageIndex}/{totalImgs} image of link {pageUrl}----------")
            print(f"fetching {imageIndex}/{totalImgs} image of link {pageUrl}----------")
            res = returnImage(item["src"],newImageName,logger=logger)
            if(res):
                logger.info(f"image {imageIndex}/{totalImgs} image of link {pageUrl} returned")
                imagesList.append(res)
            else:
                logger.info(f"image {imageIndex}/{totalImgs} image of link {pageUrl} not returned")
            
        return imagesList
        pass
    except Exception as e:
        logger.error(f"Error Scraping single chapter : {e}")

def fetchChapterData(url,logger=setup_logger(DEFAULT_LOGGER,DEFAUL_LOG_FILE)):
    texts = url.split("/")
    chaptername = texts[-2]
    chapterNameSplit = chaptername.split('-')
    nums = []
    for _ in chapterNameSplit:
        if(_.isdigit()):
            nums.append(int(_))
    chapterno = 0.0
    # print("len",len(nums))
    # print(nums)
    # print(len(nums) >= 2)
    if(len(nums) >= 2):
        # print("here")
        # print(nums[-1])
        # print(nums[-2])
        temp = str(nums[-2]) +'.' + str(nums[-1])
        # print("temp ",temp)
        # print(float(temp))
        # print("str ",str(nums[-1]) + '.' + nums[-1])
        chapterno = temp #float(str(nums[-2]) + '.' + nums[-1])
    else:
        chapterno = int(str(nums[-1]))
    # print(chapterno)
    
    return [chapterno,chaptername]


def fetchChaptersLink(pageUrl,startPageNo = 0,endPageNo = -1,logger=setup_logger(DEFAULT_LOGGER,DEFAUL_LOG_FILE)):
    startPageNo = max(0,startPageNo)
    response = requests.get(pageUrl,verify = False)
    soup = BeautifulSoup(response.text, "html.parser")
    maxChilds = 0
    listUl = []
    uls = soup.find_all("ul")
    for ul in uls:
        if(maxChilds < len(list(ul.children))):
            maxChilds = len(list(ul.children))
            listUl = ul

    
    links = []
    for child in listUl.children:
        try:
            if((child.find('a') != None) and (len(list(child.children)) == 1)):
                linktag = child.find('a')
                chapterLink = linktag['href']
                [chapterNo,chapterName] = fetchChapterData(url = chapterLink,logger = logger) 
                # print(chapterNo," ",chapterName)
                if((float(startPageNo) <= float(chapterNo)) 
                   and ((float(chapterNo) <= (float(endPageNo) + 1.0)) or (endPageNo == -1))):
                    links.append([chapterLink,chapterName])
                    # print("chap no ",chapterNo," ",startPageNo," ",endPageNo)
                    logger.info(f"selected chapter with chapter name {chapterName} and chapterNo {float(chapterNo)}")
        except:
            pass
    links.reverse()
    return links




def scrapChapters(_startIndex,_endIndex,chapterslink,folderName=""):
    # print("start ",start," end ",end)
    thName = threading.current_thread().name
    logFileBaseFolder = os.path.join("Logs",folderName)
    os.makedirs(logFileBaseFolder, exist_ok=True)
    log_file = os.path.join(logFileBaseFolder, f"thread_{thName}.log")
    # log_file = os.path.join("Logs",log_file)
    logger = setup_logger(f"Thread-{thName}", log_file)
    logger.info(f"Downloading links from {_startIndex} to {_endIndex}")
    try:
        for index in range(_startIndex,_endIndex+1):
            if(index >= len(chapterslink)):
                break
            # pdfName = "Chapter-"+str(chapter)+".pdf"
            pdfName = "Chapter" + str(chapterslink[index][0]) + ".pdf"
            logger.info(f"creating {pdfName} in thread {thName}..........................")
            print(f"creating {pdfName} in thread {thName}..........................")
            imageList = scrapSingleChapter(chapterslink[index][0],logger=logger)
            images_bin_to_pdf(image_paths=imageList,output_folder=folderName,output_pdf=pdfName,logger=logger)
            time.sleep(1)
            pass
        pass
    except KeyboardInterrupt:
        logger.error("\nCtrl+C detected! Exiting gracefully.")
        print("\nCtrl+C detected! Exiting gracefully.")



def downloadManga(mangaName,url,startPageNo=-1,endPageNo = -1,logger=setup_logger(DEFAULT_LOGGER,DEFAUL_LOG_FILE),threadCount = 4):
    logger.info(f"chapters from {startPageNo} to {endPageNo} will be downloaded")
    chaptersLinksArray = fetchChaptersLink(url,startPageNo,endPageNo,logger)
    linksCount = len(chaptersLinksArray)
    threads = []
    start = 0
    print(f"{linksCount} chapters found")
    logger.info(f"{linksCount} chapters found")
    gap = 50
    gap = int((linksCount/threadCount))+1
    while(start < (linksCount)):
        end = min(start + gap,linksCount-1)
        threadname = "thread" + str(start) + "to" + str(end)
        firstChapterName = chaptersLinksArray[start][0]
        secondChapterName = chaptersLinksArray[end][0]
        logger.info(f"Thread named {threadname} started to donwload from {firstChapterName} to {secondChapterName}")
        t = threading.Thread(target=scrapChapters,name = threadname ,args=(start,end,chaptersLinksArray,mangaName))
        threads.append(t)
        t.daemon = False
        t.start()
        start = start + gap + 1

    for t in threads:
        t.join()

def countChapters(url):
    return len(fetchChaptersLink(url))
    

    
# # Read JSON file and convert it to a dictionary
with open("docs\mangaLinks1.json", "r") as file:
    data = json.load(file)  # Convert JSON to dict

# # Print dictionary
# print(data)

log_file = f"thread_MAIN.log"
logger = setup_logger(f"thread_MAIN.log", log_file)
for mangaName in data:
    logger.info(f"Downloading Manga {mangaName} from url {data[mangaName][0]} ")
    downloadManga(mangaName=mangaName,url = data[mangaName][0],startPageNo=0,endPageNo=1000,logger = logger)
    # break

    


