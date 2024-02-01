from bs4 import BeautifulSoup
import requests

def comestible(url):
    res = ""
    categories = ["/poisonous","/edible","/inedible"]
    k2soup = BeautifulSoup(requests.get(url).content, "html.parser")
    try :
        page = k2soup.find("div", class_="cat_link")
        link = page.find('a').get('href')
        for category in categories:
            if category in link:
                res = str.upper(category[1])
                break
        return res
    except :
        return ""
    
def color(url):
    k2soup = BeautifulSoup(requests.get(url).content, "html.parser")
    try :
        page = k2soup.find("div", class_="mprofile")
        color_tag = page.find('strong', string='Color:')
        colors = [link.text for link in color_tag.find_next_siblings('a')]
        res = ""
        for i in range(len(colors)):
            if i == len(colors) -1:
                res += colors[i]
            else:
                res += colors[i] + "-"
        return res
    except :
        return ""

#How do I handle multiple shapes ? (Not specified in subject) (https://ultimate-mushroom.com/edible/1001-agaricus-benesii.html)
#I guess I will have to change it to handle it like colors and separating them with "-"
def shape(url):
    k2soup = BeautifulSoup(requests.get(url).content, "html.parser")
    try :
        page = k2soup.find("div", class_="mprofile")
        shape_tag = page.find('strong', string='Shape:')
        shape = shape_tag.find_next_siblings('a')[0].text
        str_list = shape.split(" ")
        res = ""
        for str_part in str_list:
            res += str_part
        return res
    except :
        return ""
    
def surface(url):
    k2soup = BeautifulSoup(requests.get(url).content, "html.parser")
    try :
        page = k2soup.find("div", class_="mprofile")
        surface_tag = page.find('strong', string='Surface:')
        surface = surface_tag.find_next_siblings('a')[0].text
        str_list = surface.split(" ")
        res = ""
        for str_part in str_list:
            res += str_part
        return res
    except :
        return ""
    
#Figure out what to do when one or more of the calls returns "" (Not specified in subject)
def csv(url):
    return comestible(url) +","+ color(url) +","+ shape(url) +","+surface(url)


def scrap():
    file = open('champignons.csv', 'w')
    site_url = "https://ultimate-mushroom.com/mushroom-alphabet.html"
    k2soup = BeautifulSoup(requests.get(site_url).content, "html.parser")
    try :
        page = k2soup.find("ol")
        a_tags = page.find_all('a')
        for a_tag in a_tags:
            link = a_tag.get('href')
            data = csv(link)
            print(data)
            file.write(data+"\n")
            file.flush()
    except :
        print("Something went wrong while scrapping website")
    file.close()
    


scrap()