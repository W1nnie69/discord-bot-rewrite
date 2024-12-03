import json



def rmJsonVal():
    with open("temp-ytlist.json", "r") as file:
        data = json.load(file)

    for i in range(1,11):
        data.pop(str(i))

    with open("temp-ytlist.json", "w") as file2:
        json.dump(data, file2, indent=4)



def isJsonEmpty():
    with open("temp-ytlist.json", "rb") as file:
        data = json.load(file)
    
    if not data:
        print("json empty")
        return True
    
    else:
        print("json is not empty")
        return False