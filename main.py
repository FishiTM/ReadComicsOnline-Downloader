import os
import sys
import shutil
import requests
from lxml import etree
from bs4 import BeautifulSoup
from PIL import Image
from time import perf_counter

def setTitle(s):
    if (os.name == "nt"):
        os.system(f"title {s}")
    else:
        sys.stdout.write(f"\x1b]2;{s}\x07")
        
def clearConsole():
    if (os.name == "nt"):
        os.system("cls")
    else:
        os.system("clear")

def fixURL(url): # INEFFICIENT BUT WORKS
    if (url.startswith("http://")):
        url.replace("http://", "https://")
    elif (url.startswith("www.readcomicsonline")):
        url.replace("www.readcomicsonline", "https://readcomicsonline")
    elif (url.startswith("readcomicsonline.")):
        url.replace("readcomicsonline.", "https://www.readcomicsonline.")
    return url

def getComicName(baseUrl: str):
    return baseUrl.replace("https://", "").split("/")[2].replace("-", " ").title() # 0=Domain 1=Type 2=Title 3=BookNo 4=Page

def setPageNo(url, n):
    splitURL = url.split("/")
    splitURL[-1] = str(n)
    return "/".join(splitURL)

def setPageDefault(url):
    if (not url.endswith("/")):
        url = url + "/"
    t = url.replace("https://", "").split("/")
    if (len(t) != 5):
        if (not url.endswith("/")):
            url = url + "/"
        url = url + "1"
    return setPageNo(url, 1)

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

def getComicPageImg(baseUrl: str, n: int):
    t = baseUrl.replace("https://", "").split("/")[-1].split(".")
    fn, ext = t[0], t[1]
    s = str(n)
    while (len(s) < len(fn)):
        s = "0" + s
    ret = baseUrl.replace("https://", "").split("/")
    ret[-1] =f"{s}.{ext}"
    return "https://" + "/".join(ret)

def resetTempFolder():
    deleteTempFolder()
    os.mkdir("./temp/")

def deleteTempFolder():
    try:
        shutil.rmtree("./temp/")
    except Exception:
        pass

def dirSize(path: str):
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += dirSize(entry.path)
    return total

def calcDLSpeed(fp, t1, t2):
    fs = dirSize(fp)
    speed = fs / (t2-t1)
    return speed # IN BITS

def nextOutput():
    if (not os.path.exists("./output.pdf")):
        return "./output.pdf"
    i = 1
    while (True):
        if (not os.path.exists(f"./output ({i}).pdf")):
            return f"./output ({i}).pdf"
        i+=1

clearConsole(); setTitle("ReadComicsOnline Downloader")
baseURL = input("Comic URL : ").strip()
clearConsole()
baseURL = fixURL(baseURL); baseURL = setPageDefault(baseURL)

resetTempFolder()
comicName = getComicName(baseURL); print(f"Downloading '{comicName}'\n")
i = 1; start_time = perf_counter();
baseImage = getComicPage(baseURL, 1)
while (True):
    try:
        image = getComicPageImg(baseImage, i)
    except:
        break
    if (image is not None):
        r = requests.get(image, allow_redirects=True)
        if r.status_code == 404:
            break
        fn = image.split("/")[-1]
        fp = f"./temp/{fn}"
        open(fp, 'wb').write(r.content)
        print(f"Downloaded {i} Pages @ {round(calcDLSpeed('./temp/', start_time, perf_counter()) / 1000 / 1000,2)} Mb/s   ", end="\r")
    else:
        break
    i+=1

files = os.listdir("./temp/"); files.sort()
ext = "." + files[0].split(".")[-1]
images = []
outfile = nextOutput()
im = Image.open(f"./temp/{files[0]}")
if im.mode == "RGBA":
    im = im.convert("RGB")
im.save(outfile, save_all=True, quality=100, append_images=images[1:])
i = 1; start_time = perf_counter(); print(f"\n\nConverted {i} Pages To PDF @ {round(i/(perf_counter()-start_time),2)} Pages/s", end="\r")
im.close()
for file in files[1:]:
    file = f"./temp/{file}"
    im = Image.open(file)
    if im.mode == "RGBA":
        im = im.convert("RGB")
    im.save(outfile, quality=100, append=True)
    print(f"Converted {i} Pages To PDF @ {round(i/(perf_counter()-start_time),2)} Pages/s     ", end="\r")
    im.close()
    i+=1
print(f"Converted {i} Pages To PDF @ {round(i/(perf_counter()-start_time),2)} Pages/s     ")
print("\nDone Converting!")
deleteTempFolder()
