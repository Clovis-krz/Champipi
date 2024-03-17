import numpy as np
from bs4 import BeautifulSoup
import requests
import pandas as pd

"""
 Returns the first letter of the type from a given mushroom page.
 "P": Poisonous
 "E": Edible
 "I": Inedible
 "": Default value used if the provided page is incorrect

 @param str url The URL of a mushroom page
"""
def comestible(url):
    scraper = BeautifulSoup(requests.get(url).content, "html.parser")
    categories = ["/poisonous","/edible","/inedible"]
    try:
        page = scraper.find("div", class_="cat_link")
        link = page.find('a').get('href')

        for category in categories:
            if category in link: return str.upper(category[1])

        return ""
    except: return ""


"""
 Returns the mushroom color from a given mushroom page.
 Or an empty string if the provided page is incorrect.

 @param url The URL of a mushroom page
"""
def color(url):
    scraper = BeautifulSoup(requests.get(url).content, "html.parser")
    try:
        page = scraper.find("div", class_="mprofile")
        colorTag = page.find('strong', string='Color:')
        colors = [link.text for link in colorTag.find_next_siblings('a')]

        res = ""
        for i in range(len(colors)):
            res += colors[i]
            if i != (len(colors) - 1): res += "-"

        return res
    except: return ""


"""
 Returns the mushroom shape from a given mushroom page.
 Or an empty string if the provided page is incorrect.

 @param url The URL of a mushroom page
"""
def shape(url):
    def removeDashesAndCapitalizeLetters(string):
        splitted = string.replace('-', ' ').split()

        res = ""
        for i in splitted: res += i.capitalize()

        return res

    scraper = BeautifulSoup(requests.get(url).content, "html.parser")
    try:
        page = scraper.find("div", class_="mprofile")
        shapeTag = page.find('strong', string='Shape:')
        shapes = [link.text for link in shapeTag.find_next_siblings('a')]

        res = ""
        for i in range(len(shapes)):
            res +=  removeDashesAndCapitalizeLetters(shapes[i])
            if i != (len(shapes) - 1): res += "-"
                
        return res
    except: return ""


"""
 Returns the mushroom surface from a given mushroom page.
 Or an empty string if the provided page is incorrect.

 @param url The URL of a mushroom page
"""
def surface(url):
    scraper = BeautifulSoup(requests.get(url).content, "html.parser")
    try:
        page = scraper.find("div", class_="mprofile")
        surfaceTag = page.find('strong', string='Surface:')
        surfaceString = surfaceTag.find_next_siblings('a')[0].text
        stringList = surfaceString.split(" ")

        res = ""
        for stringPart in stringList: res += stringPart

        return res
    except: return ""


"""
 Creates a CSV-formatted line from the given URL
"""
def csv(url):
    return comestible(url) + "," + color(url) + "," + shape(url) + "," + surface(url)


"""
 Part 1: Creating the CSV data from the ultimate-mushroom.com website using beautifulsoup
"""
def part1():
    file = open('champignons.csv', 'w')
    file.write("Edible,Color,Shape,Surface\n")
    file.flush()

    url = "https://ultimate-mushroom.com/mushroom-alphabet.html"
    scraper = BeautifulSoup(requests.get(url).content, "html.parser")

    try:
        page = scraper.find("div", class_="full_text")
        pageLinks = page.find_all('a')

        for tag in pageLinks:
            link = tag.get('href')
            if "https://ultimate-mushroom.com" in link:
                data = csv(link)
                print("Added line: " + data)
                file.write(data + "\n")
                file.flush()
    except: print("Something went wrong while scrapping the website.")

    file.close()


"""
 Formats the Edible column of a given mushroom dataframe
"""
def formatEdibleColumn(mushrooms):
    print("Initial CSV data info:")
    print(mushrooms.info())

    print("\nInitial edible data:")
    print(mushrooms["Edible"].value_counts())

    # Formatting
    mushrooms["Edible"] = mushrooms["Edible"].replace({"E": 0, "I": 1, "P": 2}).fillna(-1)

    print("\nFirst 10 values:")
    for i in range(10): print(mushrooms["Edible"][i])

    print("\nEdible data after formatting:")
    print(mushrooms["Edible"].value_counts())


"""
 Formats the Shape and Surface columns of a given mushroom dataframe
"""
def formatShapeAndSurfaceColumns(mushrooms):
    # pd.unique(X) prends une collection X et renvoit une nouvelle collection sans doublons
    # champignons["Shape"].str convertit la colonne Shape en string
    # split("-") sépare les strings qui incluent "-" en plusieurs sous-strings
    # explode() crée une colonne à partir de la collection, utilisée par dropna()
    # dropna() supprime les valeurs vides
    shapes = pd.unique(mushrooms["Shape"].str.split("-").explode().dropna())

    for s in shapes:
        mushrooms[s] = mushrooms["Shape"].astype(str).str.contains(s).astype(int)

    surfaces = pd.unique(mushrooms["Surface"].explode().dropna())
    for s in surfaces:
        mushrooms[s] = mushrooms["Surface"].astype(str).str.contains(s).astype(int)

    mushrooms.drop(columns=["Shape", "Surface"], inplace=True)

    print("\nCSV table size after handling the shapes and surfaces:")
    print(mushrooms.shape)


"""
 Formats the color column of a given mushroom dataframe
"""
def formatColorColumn(mushrooms):
    print("\nAmount of separate colors:")
    colorNames = pd.unique(mushrooms["Color"].str.split("-").explode().dropna())
    print(len(colorNames))

    R = [219, 255, 255, 165, 255, 128, 210, 255, 128, 255,   0,   0,   0, 238, 231]
    G = [112, 255, 255,  42, 192,   0, 180, 165, 128,   0,   0, 255,   0, 130, 209]
    B = [147, 255,   0,  42, 203, 128, 140,   0, 128,   0,   0,   0, 255, 238, 255]
    colorMap = pd.DataFrame({"Color": colorNames, "R": R, "G": G, "B": B})

    colors = pd.DataFrame({"Color": pd.unique(mushrooms["Color"].explode().dropna())})

    colors[['Color1', 'Color2']] = colors['Color'].str.split('-', expand=True)

    colors = colors.merge(colorMap, left_on="Color1", right_on="Color", how="left").merge(colorMap, left_on="Color2", right_on="Color", suffixes=("_1", "_2"), how="left")

    colors["R"] = colors[["R_1", "R_2"]].mean(axis=1)
    colors["G"] = colors[["G_1", "G_2"]].mean(axis=1)
    colors["B"] = colors[["B_1", "B_2"]].mean(axis=1)
    colors["Color"] = colors["Color_x"]
    colors = colors[["Color", "R", "G", "B"]]

    mushroomsMerged = mushrooms.merge(colors, left_on="Color", right_on="Color", how="left").fillna(-255)
    mushrooms["R"] = mushroomsMerged["R"]
    mushrooms["G"] = mushroomsMerged["G"]
    mushrooms["B"] = mushroomsMerged["B"]
    mushrooms.drop(columns=["Color"], inplace=True)

    print("\nData after transformation:")
    print(mushrooms)


"""
 Part 2: Converting the CSV data to numerical values using pandas
"""
def part2():
    # Stops pandas from being annoying about future updates.
    pd.set_option('future.no_silent_downcasting', True)

    mushrooms = pd.read_csv("champignons.csv")

    formatEdibleColumn(mushrooms)
    formatShapeAndSurfaceColumns(mushrooms)
    formatColorColumn(mushrooms)

    return mushrooms


"""
 Main function of the program
"""
if __name__ == "__main__":
    print("===== PART 1: Creating the CSV data from the ultimate-mushroom.com website using beautifulsoup =====")
    #part1()

    print("===== PART 2:  Converting the CSV data to numerical values using pandas =====")
    data = part2()

