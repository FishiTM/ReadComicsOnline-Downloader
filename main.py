import os
import sys
import shutil
import requests
from lxml import etree
from bs4 import BeautifulSoup
from PIL import Image

def clearConsole():
    if (os.name == "nt"):
        os.system("cls")
    else:
        os.system("clear")

def fixURL(URL): # INEFFICIENT BUT WORKS
    if (URL.startswith("http://")):
        URL.replace("http://", "https://")
    elif (URL.startswith("www.readcomicsonline")):
        URL.replace("www.readcomicsonline", "https://readcomicsonline")
    elif (URL.startswith("readcomicsonline.")):
        URL.replace("readcomicsonline.", "https://www.readcomicsonline.")
    return URL

def setPageNo(URL, n):
    splitURL = URL.split("/")
    splitURL[-1] = str(n)
    return "/".join(splitURL)

def getComicPage(baseURL, n):
    URL = setPageNo(baseURL, n)
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    dom = etree.HTML(str(soup))
    src = dom.xpath("//*[@id=\"ppp\"]/a/img")[0]
    try:
        return str(src.attrib["src"]).strip()
    except:
        return None

def deleteTempFolder():
    try:
        shutil.rmtree("./temp/")
    except Exception:
        pass

def resetTempFolder():
    deleteTempFolder()
    os.mkdir("./temp/")

def setTitle(s):
    if (os.name == "nt"):
        os.system(f"title {s}")
    else:
        sys.stdout.write(f"\x1b]2;{s}\x07")

def getComicName(baseURL):
    t = baseURL.replace("https://", "").split("/")  # 0=Domain 1=Type 2=Title 3=BookNo 4=Page
    name = t[2].replace("-", " ").title()
    return name

clearConsole()
setTitle("ReadComicsOnlineDL - Menu")
baseURL = input("Comic URL : ").strip()
clearConsole()
baseURL = fixURL(baseURL)
baseURL = setPageNo(baseURL, 1)
resetTempFolder()

comicName = getComicName(baseURL)
print(f"Downloading '{comicName}'")
setTitle("ReadComicsOnlineDL - Downloading")
i = 1; images = []
while (True):
    try:
        image = getComicPage(baseURL, i)
    except:
        break
    if (image is not None):
        r = requests.get(image, allow_redirects=True)
        fn = image.split("/")[-1]
        fp = f"./temp/{fn}"
        open(fp, 'wb').write(r.content)
        images.append(fp)
        setTitle(f"ReadComicsOnlineDL - Downloaded {i} Pages")
    else:
        break
    i+=1
print("Done Downloading!")
images.sort()

print("Converting To PDF...")
setTitle(f"ReadComicsOnlineDL - Converting To PDF")
ext = "." + images[0].split(".")[-1]
imagelist = []
for fp in images:
    im = Image.open(fp)
    if im.mode == "RGBA":
        im = im.convert("RGB")
    imagelist.append(im)
imagelist[0].save("./output.pdf", save_all=True, quality=100, append_images=imagelist[1:])
print("Done Converting!")
setTitle(f"ReadComicsOnlineDL - Cleaning Temp File")
deleteTempFolder()
setTitle(f"ReadComicsOnlineDL - Finished")