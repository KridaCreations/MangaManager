# https://www.google.com/about/careers/applications/jobs/results?target_level=EARLY&degree=BACHELORS&location=India


import requests
from bs4 import BeautifulSoup, Tag
from PIL import Image
import re
import io
import threading
import time
import logging
import os
import json
import sys
import certifi
import asyncio
# import aiohttp



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
        
        # for image in images:
        #     new_size = (image.width//2,image.height //2)
        #     image = image.resize(new_size,Image.Resampling.LANCZOS)

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
        print(f"Error: {e} ")
        logger.info(f"error while creatign output pdf {output_pdf} the error is {e}")


def returnImage(url, filename="downloaded_image.jpg",logger=setup_logger(DEFAULT_LOGGER,DEFAUL_LOG_FILE)):
    try:
        response = requests.get(url, stream=True, verify=certifi.where(),timeout=10)
        response.raise_for_status()  # Raise error for bad responses (4xx and 5xx)

        if "image" not in response.headers.get("Content-Type", ""):
            print("Error: Response is not an image!")
        else:
            # img = Image.open(BytesIO(response.content))
            # img.show()
            return response.content

        # with open(filename, "wb") as file:
        #     file.write(response.content)
        return response.content
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading image: {e}")
        print(f"Error downloading image: {e}")
        return False

def scrapSingleChapter(pageUrl,folderName = "",logger=setup_logger(DEFAULT_LOGGER,DEFAUL_LOG_FILE)):
    logger.info(f"requesting the data for page {pageUrl}")
    try:
        proxy = {
            "http": "http://127.0.0.1:8080",
            "https": "http://127.0.0.1:8080",
        }


        response = requests.get(pageUrl,verify=certifi.where(),proxies=proxy)
        soup = BeautifulSoup(response.text, "html.parser")

        imgs = soup.find_all('img')
        totalImgs = len(list(imgs))
        imageIndex = 0
        imageBaseName = "image"
        imagesList = []
        for item in imgs:
            imageIndex += 1
            newImageName = imageBaseName + str(imageIndex) + ".jpg"
            # if("http" in item["src"]):
                # print(item[:4])
            if(item["src"].startswith("http")):
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
    if(len(nums) >= 2):
        temp = str(nums[-2]) +'.' + str(nums[-1])
        chapterno = temp #float(str(nums[-2]) + '.' + nums[-1])
    else:
        chapterno = int(str(nums[-1]))
    
    return [chapterno,chaptername]

def fetchChaptersLink2(pageUrl,startPageNo = 0,endPageNo = -1,logger=setup_logger(DEFAULT_LOGGER,DEFAUL_LOG_FILE)):
    startPageNo = max(0,startPageNo)
    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        # response = requests.get(pageUrl,verify=certifi.where(),proxies=proxy)
    response = requests.get(pageUrl,verify=certifi.where(),headers=headers)
    print(response.text)
    soup = BeautifulSoup(response.text, "html.parser")

    rawlinks = soup.find_all('a')

    cleanlinks = []
    for link in rawlinks:
        linkText = link.text.lower()
        if "chapter" in linkText:
            if linkText not in cleanlinks:
                cleanlinks.append(link['href'])
                print(link['href'])

    result = []
    for link in cleanlinks:
        try:
            [chapterNo,chapterName] = fetchChapterData(url = link,logger = logger) 
            print(f"chapter name {chapterNo}")
            if((float(startPageNo) <= float(chapterNo)) 
            and ((float(chapterNo) <= (float(endPageNo) + 1.0)) or (endPageNo == -1))):
                result.append([link,str(chapterNo)])
                logger.info(f"selected chapter with chapter name {chapterName} and chapterNo {float(chapterNo)}")
                # print("chapter link ",chapterLink)



        except:
            print("error when fetching chapter data")
            logger.error("error when fetching chapter data")

    return result
    pass



# def fetchChaptersLink(pageUrl,startPageNo = 0,endPageNo = -1,logger=setup_logger(DEFAULT_LOGGER,DEFAUL_LOG_FILE)):
#     try:
#         startPageNo = max(0,startPageNo)
#         print("here -----------------")
#         print("page url ",pageUrl)

#         proxy = {
#             "http": "http://127.0.0.1:8080",
#             "https": "http://127.0.0.1:8080",
#         }

#         headers = {
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
#         }
#         # response = requests.get(pageUrl,verify=certifi.where(),proxies=proxy)
#         response = requests.get(pageUrl,verify=certifi.where(),headers=headers)
#         # print(response.text)
#         response.raise_for_status()
#         print("here -----------------")
#         soup = BeautifulSoup(response.text, "html.parser")
        
#         maxChilds = 0
#         listUl = []
#         uls = soup.find_all("ul")
#         for ul in uls:
#             if(maxChilds < len(list(ul.children))):
#                 maxChilds = len(list(ul.children))
#                 listUl = ul
                

        
#         print(listUl.contents)
#         links = []
#         for child in listUl.children:
#             try:
#                 # print("ter--------------------------------")
#                 # print(str(child))
#                 # print(type(child))
#                 # print(isinstance(child,Tag))
#                 # print(child.find('a') != None)
#                 # print(len(list(child.children)) == 1)
#                 # print("childcount ",len(list(child.children)))
#                 # temp = list(child.children)
#                 # for _ in temp:
#                 #     print(str(_))
#                 if(isinstance(child,Tag) and (child.find('a') != None) ):
#                     linktag = child.find('a')
#                     chapterLink = linktag['href']
#                     print("chapter link  ",chapterLink)
#                     [chapterNo,chapterName] = fetchChapterData(url = chapterLink,logger = logger) 
#                     # print(chapterNo)
#                     if((float(startPageNo) <= float(chapterNo)) 
#                     and ((float(chapterNo) <= (float(endPageNo) + 1.0)) or (endPageNo == -1))):
#                         links.append([chapterLink,str(chapterNo)])
#                         logger.info(f"selected chapter with chapter name {chapterName} and chapterNo {float(chapterNo)}")
#             except:
#                 pass
#         links.reverse()
#         return links
#     except Exception as e:
#         logger.error(f"error fetching chapter links {e}")
#         return False

# def fetchChaptersLink(pageUrl,startPageNo = 0,endPageNo = -1,logger=setup_logger(DEFAULT_LOGGER,DEFAUL_LOG_FILE)):
#     startPageNo = max(0,startPageNo)
#     print("here -----------------")
#     response = requests.get(pageUrl,verify=False)
#     print("here -----------------")
#     print(response.text)
#     soup = BeautifulSoup(response.text, "html.parser")
#     maxChilds = 0
#     listUl = []
#     uls = soup.find_all("ul")
#     for ul in uls:
#         # print(ul)
#         if(maxChilds < len(list(ul.children))):
#             maxChilds = len(list(ul.children))
#             print(len(list(ul.children)))
#             listUl = ul

#     # print(f{{}})
#     links = []
#     # print(list(listUl.children))
#     for child in listUl.children:
#         try:
#             # print("child     ",child)
#             if((child != None) and(child.find_all('a') != None)):# and (len(list(child.children)) == 1)):
#                 # print("looking for link")
#                 linktag = child.find_all('a')[0]
#                 chapterLink = linktag['href']
#                 try:
#                     [chapterNo,chapterName] = fetchChapterData(url = chapterLink,logger = logger) 
#                     print(f"chapter name {chapterNo}")
#                     if((float(startPageNo) <= float(chapterNo)) 
#                     and ((float(chapterNo) <= (float(endPageNo) + 1.0)) or (endPageNo == -1))):
#                         links.append([chapterLink,str(chapterNo)])
#                         logger.info(f"selected chapter with chapter name {chapterName} and chapterNo {float(chapterNo)}")
#                         # print("chapter link ",chapterLink)
#                 except:
#                     print("wrong link ")


#         except:
#             print("error when fetching chapter data")
#             logger.error("error when fetching chapter data")
#     links.reverse()
#     return links

def fetchChaptersLink2(pageUrl,startPageNo = 0,endPageNo = -1,logger=setup_logger(DEFAULT_LOGGER,DEFAUL_LOG_FILE)):
    startPageNo = max(0,startPageNo)
    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
#         # response = requests.get(pageUrl,verify=certifi.where(),proxies=proxy)
    response = requests.get(pageUrl,verify=certifi.where(),headers=headers)
    print(response.text)
    soup = BeautifulSoup(response.text, "html.parser")

    rawlinks = soup.find_all('a')

    cleanlinks = []
    for link in rawlinks:
        linkText = link.text.lower()
        if "chapter" in linkText:
            if linkText not in cleanlinks:
                cleanlinks.append(link['href'])
                print(link['href'])

    result = []
    for link in cleanlinks:
        try:
            [chapterNo,chapterName] = fetchChapterData(url = link,logger = logger) 
            print(f"chapter name {chapterNo}")
            if((float(startPageNo) <= float(chapterNo)) 
            and ((float(chapterNo) <= (float(endPageNo) + 1.0)) or (endPageNo == -1))):
                result.append([link,str(chapterNo)])
                logger.info(f"selected chapter with chapter name {chapterName} and chapterNo {float(chapterNo)}")
                # print("chapter link ",chapterLink)



        except:
            print("error when fetching chapter data")
            logger.error("error when fetching chapter data")

    return result
    pass
# >>>>>>> 23711a314dd50de5606c399c737d3286d8a79127




def scrapChapters(_startIndex,_endIndex,chapterslink,folderName=""):
    thName = threading.current_thread().name
    logFileBaseFolder = os.path.join("Logs",folderName)
    os.makedirs(logFileBaseFolder, exist_ok=True)
    log_file = os.path.join(logFileBaseFolder, f"thread_{thName}.log")
    logger = setup_logger(f"Thread-{thName}", log_file)
    logger.info(f"Downloading links from {_startIndex} to {_endIndex}")
    try:
        for index in range(_startIndex,_endIndex+1):
            if(index >= len(chapterslink)):
                break
            # pdfName = "Chapter-"+str(chapter)+".pdf"
            pdfName = "Chapter" + str(chapterslink[index][1]) + ".pdf"
            # print(pdfName)
            logger.info(f"creating {pdfName} in thread {thName}..........................")
            print(f"creating {pdfName} in thread {thName}..........................")
            imageList = scrapSingleChapter(chapterslink[index][0],logger=logger)
            images_bin_to_pdf(image_paths=imageList,output_folder=folderName,output_pdf=pdfName,logger=logger)
            time.sleep(1)
            pass
        pass
    except KeyboardInterrupt:
        # return False
        logger.error("\nCtrl+C detected! Exiting gracefully.")
        print("\nCtrl+C detected! Exiting gracefully.")



def downloadManga(mangaName,url,startChapterNo=-1,endChapterNo = -1,logger=setup_logger(DEFAULT_LOGGER,DEFAUL_LOG_FILE),threadCount = 4):
    logger.info(f"chapters from {startChapterNo} to {endChapterNo} will be downloaded")
    chaptersLinksArray = fetchChaptersLink2(url,startChapterNo,endChapterNo,logger)
    print("final links")
    # print(chaptersLinksArray)
    linksCount = len(chaptersLinksArray)
    threads = []
    print(f"{linksCount} chapters found")
    logger.info(f"{linksCount} chapters found")
    # gap = 50
    start = 0
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
    return len(fetchChaptersLink2(url))
    


    
# Read JSON file and convert it to a dictionary
with open("..\docs\mangaLinks1.json", "r") as file:
    data = json.load(file)  # Convert JSON to dict

# # Print dictionary
# print(data)

log_file = f"thread_MAIN.log"
logger = setup_logger(f"thread_MAIN.log", log_file)
for mangaName in data:
    logger.info(f"Downloading Manga {mangaName} from url {data[mangaName][0]} ")
    downloadManga(mangaName=mangaName,url = data[mangaName][0],startChapterNo=0,endChapterNo=1000,logger = logger,threadCount=8)
    break

    


