import subprocess
import requests as req
import json
from pathlib import Path
from os import mkdir, remove
from re import sub
from shutil import copytree, ignore_patterns, rmtree

def Split(word): 
    return [char for char in word]  

def main():
    if not Path("./Repositories").is_dir() and not Path("./temp").is_dir():
        mkdir("./Repositories")
        mkdir("./temp")
    try:
        addons = json.loads(open("addons.json").read())
        tbl = open("settings.txt").read().split("\n")
        gmad = tbl[0]
        gmpublish = tbl[1]
    except:
        print("Please run \"setup.py\" first.")
        exit()
    dirPath = Path(__file__).parent.absolute()
    for addon in addons:
        data = addons[addon]
        if (data[1] != ""):
            repoName = data[1].split("/")[1]
            #Update the git-repo if necessary
            date = req.get("https://api.github.com/repos/" + data[1]).json()["updated_at"]
            if date != data[2]:
                if Path("./Repositories/" + repoName).is_dir():
                    subprocess.call("git -C ./Repositories/{}/ pull".format(repoName))
                else:
                    subprocess.call("git -C ./Repositories/ clone https://github.com/{}.git".format(data[1]))
                addons[addon][2] = date
                #
                #Publish the addon to the workshop, when out of date
                #
                copytree("./Repositories/" + repoName, "./temp/" + repoName, ignore=ignore_patterns(".git", "*.md")) #filter for different files
                #Create addon.json file
                db = {}
                addonType = {0: "ServerContent", 1: "gamemode", 2: "map", 3: "weapon", 4: "vehicle", 5: "npc", 6: "tool", 7: "effects", 8: "model"}
                addonTag = {0: "fun", 1: "roleplay", 2: "scenic", 3: "movie", 4: "realism", 5: "cartoon", 6: "water", 7: "comic", 8: "build"}
                title = data[0]
                title = sub(r"\"\b", "", title)
                title = sub(r"\b\"", "", title)
                db["title"] = title
                for name in addonType:
                    print("[{}] {}".format(name, addonType[name]))
                typeInput = input("\nPlease choose your type of addon for {} (0-8): ".format(data[0]))
                for name in addonTag:
                    print("[{}] {}".format(name, addonTag[name]))
                tagInput = input("\nPlease choose up to two tags (00-88): ")
                tagArray = []
                for char in Split(tagInput):
                    tagArray.append(addonTag[int(char)])
                try:
                    db["type"] = addonType[int(typeInput)]
                    db["tags"] = tagArray
                except:
                    db["type"] = "tool"
                    db["tags"] = ["fun", "roleplay"]
                with open("./temp/{}/addon.json".format(repoName), "w+") as addonInfo:
                    json.dump(db, addonInfo)
                #Create .gma file
                subprocess.call("{} create -folder {}/temp/{} -out {}/temp/{}.gma".format(gmad, dirPath, repoName, dirPath, repoName))
                # Publish .gma file
                changeInput = input("What are the changes of {}?:\n".format(data[0]))
                subprocess.call("{} update -id {} -addon {}/temp/{}.gma -changes \"{}\"".format(gmpublish, addon, dirPath, repoName, changeInput))
                # Delete temp files
                rmtree("./temp/" + repoName)
                remove("./temp/{}.gma".format(repoName))
        # update addons.json
        with open("./addons.json", "w") as addonsFile:
            json.dump(addons, addonsFile)
main()