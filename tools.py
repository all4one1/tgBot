import os
import sql
from datetime import datetime
from math import ceil

def log(str):
    now = datetime.now()
    daytime = now.strftime("%d/%m/%Y %H:%M:%S")
    f = open("log.txt", "a")
    f.write(daytime + ": " + str + "\n")
    f.close()


def init():
    if not os.path.exists("User"):
        os.makedirs("User")
    if not os.path.exists("log.txt"):
        f = open("log.txt","w")
        f.close()
    sql.create_db()


def to_int(str):
    i = 0
    try:
        i = int(str)
        if i < 0:
            i = -1
    except:
        i = -1
    return i
  
    

def get_current_path(id):
    return os.path.join("User",str(id),"current.txt")
    
def get_book2(path):
    book = ""
    f = open(path, "r")
    if f.readable() == True:
        book = f.read()
    return book
    
def get_book(path):
    book = ""
    f = open(path, "rb")
    if f.readable() == True:
        bytes = f.read()
        book = decode(bytes)
    return book   
    
    
def decode(bytes):
    import chardet
    try:
        info = chardet.detect(bytes)
        type = info['encoding']
        string = bytes.decode(type)
    except:
        string = "bad encoding"
    return string    
    
def get_page(book, size, pos, shift):
    text = ""
    chunk = ""
    #chunk = self.book[self.shift*x: self.shift * (1 + x)]
    text = book[pos: pos + shift]
    return chunk
    
    
def how_much_read(pos, size, shift):
    pages_read = ceil(pos / shift)
    pages_all = ceil(size / shift)
    return str(pages_read) +"/" + str(pages_all)

def how_much_percent_read(pos, size):
    return str(round(pos/size*100, 2))


def find_text(book, text):
    lc = book.lower()
    pos = lc.find(text)
    return pos

def get_token():
    token = ""
    with open('TOKEN.txt', 'r') as file:
        token = file.read()
        return token
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    #import urllib.request as urllib2
#response = urllib2.urlopen(link)
#data = response.read()
#filename = "readme.txt"
#file_ = open(filename, 'wb')
#file_.write(data)
#file_.close()
 