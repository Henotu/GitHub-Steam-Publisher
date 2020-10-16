import subprocess
from sys import exit
from re import sub
from pathlib import Path
import requests as req
import json

def Help():
    text = """
    a   reconfigure all addons
    g   edit linked GitHub repositories
    e   edit executable path (gmad.exe, gmpublish.exe)

    h   for help
    q   quit
    """
    sub("(            )", "", text)
    main()

def Quit():
    pass

def EditExecPath():
    gmad = input("Please put the path to \"gmad.exe\" here (e.g. C:\\Program Files (x86)\\Steam\\steamapps\\common\\GarrysMod\\bin\\gmad.exe):\n")
    gmpublish = input("Please put the path to \"gmpublish.exe\" here:\n")
    try:
        tbl = open("settings.txt").read().split("\n")
        tbl[0] = gmad
        tbl[1] = gmpublish
    except:
        tbl = [gmad, gmpublish]
    text = ""
    for line in tbl:
        text = text + line + "\n"
    with open("settings.txt", "w+") as stngs:
        stngs.write(text)

def GetAddons():
    gmpublish = open("settings.txt").read().split("\n")[1]
    gmpublishOutput = subprocess.check_output(gmpublish + " list")

    if b"Error:\r\n\r\nCouldn't initialize Steam!\r\nMake sure it is running!" in gmpublishOutput:
        print("Please open Steam and start again")
        exit()
    elif b"Getting published files.." in gmpublishOutput:
        addonsList = gmpublishOutput.split(b"\r\n")
        del addonsList[:5]
        del addonsList[len(addonsList) - 2:]
        temp = {}
        for addon in addonsList:
            addonInfo = addon.decode("UTF-8").split("\t")
            gitRepo = input("\nPlease put the GitHub repository belonging to {} here (e.g. Henotu/GitHub-Steam-Publisher; ENTER to skip):\n".format(addonInfo[3]))
            date = ""
            if gitRepo != "":
                utd = input("\nIs the repository up-to-date with the addon in the workshop? (y/n): ")
                if utd == "y":
                    date = req.get("https://api.github.com/repos/{}".format(gitRepo)).json()["updated_at"]
            temp[addonInfo[1]] = [addonInfo[3], gitRepo, date]
        with open("./addons.json.", "w+") as doc:
            json.dump(temp, doc)

def EditRepos():
    try:
        addons = json.loads(open("addons.json").read())
    except:
        print("The Addons are not configured")
        exit()
    print("\n")
    k = 0
    dic = {}
    for addon in addons:
        print("[{}]\t{}".format(k, addons[addon][0]))
        dic[k] = addon
        k = k + 1
    inpt = int(input("Please choose an addon to edit (0-{}): ".format(len(addons) - 1)))
    if 0 <= inpt <= (len(addons) - 1):
        inpt = dic[inpt]
        gitRepo = input("\nPlease put the GitHub repository belonging to {} here (e.g. Henotu/GitHub-Steam-Publisher; ENTER to skip):\n".format(addons[inpt][0]))
        date = ""
        if gitRepo != "":
            utd = input("\nIs the repository up-to-date with the addon in the workshop? (y/n): ")
            if utd == "y":
                date = req.get("https://api.github.com/repos/{}".format(gitRepo)).json()["updated_at"]
        addons[inpt] = [addons[inpt][0], gitRepo, date]
        with open("./addons.json.", "w+") as doc:
            json.dump(addons, doc)
        main()
    else:
        print("Invalid input. Going back to the main menu.")
        main()

def main():
    if Path("settings.txt").is_file():
        fn = {"h": Help, "g": EditRepos, "e": EditExecPath, "q": Quit, "a": GetAddons}
        cmd = input("Command (h for help): ")
        try:
            fn[cmd]()
        except:
            main()
    else:
        EditExecPath()
        GetAddons()
        main()

main()