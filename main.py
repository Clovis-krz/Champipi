import numpy as np
from bs4 import BeautifulSoup
import requests
import pandas as pd
from sklearn.discriminant_analysis import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.tree import DecisionTreeClassifier
from sklearn import tree
from joblib import dump, load
import sys

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
    mushrooms["R"] = mushroomsMerged["R"].apply(lambda x: int(round(x)))
    mushrooms["G"] = mushroomsMerged["G"].apply(lambda x: int(round(x)))
    mushrooms["B"] = mushroomsMerged["B"].apply(lambda x: int(round(x)))
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


def separate_data(dataframe):
    attributs = []
    for attribut in dataframe:
        if attribut != 'Edible':
            attributs.append(attribut)
    X_train, X_test, y_train, y_test = train_test_split(dataframe[attributs].values, dataframe["Edible"].values, test_size=0.25)
    X_train = X_train.astype('int')
    X_test = X_test.astype('int')
    y_train = y_train.astype('int')
    y_test = y_test.astype('int')
    
    return (X_train, X_test, y_train, y_test, attributs)

def train_model_svm(training_set):
    (X_train, X_test, y_train, y_test, _) = training_set

    # Initalisation et entrainement SVM
    svm = SVC()
    svm.fit(X_train, y_train)
    print("SVM accuracy:", svm.score(X_test, y_test))
    y_pred = svm.predict(X_test)
    print("SVM confusion matrix: ",confusion_matrix(y_test, y_pred))

    # Initialisation scaler et transformation de X
    scaler = StandardScaler()
    scaler.fit(X_train)
    X_train_scaler = scaler.transform(X_train)
    X_test_scaler = scaler.transform(X_test)

    # Entrainement avec scaler
    svm.fit(X_train_scaler, y_train)
    print("SVM accuracy with scaler:",svm.score(X_test_scaler, y_test))
    y_pred_scaler = svm.predict(X_test_scaler)
    print("SVM confusion matrix with scaler:",confusion_matrix(y_test, y_pred_scaler))

    return (svm, scaler)

def train_model_tree(training_set):
    (X_train, X_test, y_train, y_test, attributs) = training_set

    # Initialisation et entrainement DecisionTreeClassifier
    treeClassifier = DecisionTreeClassifier(max_depth=3)
    treeClassifier.fit(X_train, y_train)
    print("DecisionTreeClassifier accuracy:",treeClassifier.score(X_test, y_test))
    y_pred = treeClassifier.predict(X_test)
    print("DecisionTreeClassifier confusion matrix:", confusion_matrix(y_test, y_pred))

    # Initialisation scaler et transformation de X
    scaler = StandardScaler()
    scaler.fit(X_train)
    X_train_scaler = scaler.transform(X_train)
    X_test_scaler = scaler.transform(X_test)

    # Entrainement avec scaler
    treeClassifier.fit(X_train_scaler, y_train)
    print("DecisionTreeClassifier accuracy with scaler:", treeClassifier.score(X_test_scaler, y_test))
    y_pred_scaler = treeClassifier.predict(X_test_scaler)
    print("DecisionTreeClassifier confusion matrix with scaler:", confusion_matrix(y_test, y_pred_scaler))

    # Export en GraphizTree
    print("GraphizTree :")
    print(tree.export_graphviz(treeClassifier, feature_names=attributs))

    return (treeClassifier, scaler)

def save_model(model, name):
    dump(model, name+'.joblib')

def load_model(model_name):
    return load(model_name)

def parseArgs():
    cursor = 2
    rgb = []
    shape = []
    surface = []
    model_name = ""
    while cursor < len(sys.argv):
        if sys.argv[cursor] == "rgb":
            cursor += 1
            while sys.argv[cursor] != "shape":
                rgb.append(sys.argv[cursor])
                cursor += 1
        if sys.argv[cursor] == "shape":
            cursor += 1
            while sys.argv[cursor] != "surface":
                shape.append(sys.argv[cursor])
                cursor += 1
        if sys.argv[cursor] == "surface":
            cursor += 1
            while sys.argv[cursor] != "model":
                surface.append(sys.argv[cursor])
                cursor += 1
        if sys.argv[cursor] == "model":
            cursor += 1
            model_name = sys.argv[cursor]
            cursor += 1
    error = True
    if len(rgb) > 0 and len(shape) > 0 and len(surface) > 0 and len(model_name) > 0:
        error = False
    return (rgb, shape, surface, model_name, error)

def getColumnsID(param):
    columns = ['Polypore', 'Convex', 'BellShaped', 'Flat', 'Depressed',
       'CupFungi', 'CoralFungi', 'Knobbed', 'Conical', 'JellyFungi',
       'Stinkhorns', 'Earthstars', 'Bolete', 'ToothFungi', 'ShellShaped',
       'FunnelShaped', 'Puffballs', 'Corticioid', 'Chanterelles',
       'Cylindrical', 'Truffles', 'FalseMorels', 'TrueMorels', 'Cauliflower',
       'Smooth', 'FlatScales', 'Fibrous', 'Patches', 'RaisedScales', 'Hairy',
       'Powder', 'Silky', 'Velvety', 'R', 'G', 'B']
    for i in range(len(columns)):
        if columns[i] == param:
            return i
    return -1
    

def dataToMatrix(rgb, shapes, surfaces):
    to_process = np.zeros(36)
    error = False
    for i in range(len(rgb)):
        to_process[len(to_process)-1-i] = rgb[i]
    for shape in shapes:
        id = getColumnsID(shape)
        if id >= 0:
            to_process[id] = 1
        else :
            error = True
    for surface in surfaces:
        id = getColumnsID(surface)
        if id >= 0:
            to_process[id] = 1
        else :
            error = True
        
    return (to_process, error)


def process():
    (rgb, shape, surface, model_name, error) = parseArgs()
    if error:
        print("Error in the parameters of the model", rgb, shape, surface, model_name, error)
        return
    else:
        (to_process, error) = dataToMatrix(rgb, shape, surface)
        if not error:
            model = load_model(model_name + ".joblib")
            scaler = load_model(model_name + "_scaler.joblib")
            to_process_scaled = scaler.transform([to_process])
            res = model.predict(to_process_scaled)
            if res[0] == 0:
                print("EDIBLE")
            if res[0] == 1:
                print("INEDIBLE")
            if res[0] == 2:
                print("POISONOUS")
            return
        else :
            print("Error in the parameters of the model", rgb, shape, surface, model_name, error)

def part3(dataset):
    print("keys", dataset.keys())
    training_set = separate_data(dataset)
    (svm,svm_scaler) = train_model_svm(training_set)
    (treeClassifier, tree_scaler) = train_model_tree(training_set)
    save_model(svm, "SVM")
    save_model(svm_scaler, "SVM_scaler")
    save_model(treeClassifier,"TreeClassifier")
    save_model(tree_scaler, "TreeClassifier_scaler")



"""
 Main function of the program
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "process":
            process()
        elif sys.argv[1] == "part1":
            print("===== PART 1: Creating the CSV data from the ultimate-mushroom.com website using beautifulsoup =====")
            part1()
        elif sys.argv[1] == "part2-3":
            print("===== PART 2:  Converting the CSV data to numerical values using pandas =====")
            data = part2()
            print("===== PART 3:  Train DecisionTree and SVM models with transformers =====")
            part3(data)
        else:
            print("Please choose an argument between (process, part1, part2-3)")

