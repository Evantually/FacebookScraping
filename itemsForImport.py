reactionsDict = {
            "all": "total",
            "1": "like",
            "2": "love",
            "3": "wow",
            "4": "haha",
            "7": "sad",
            "8": "angry",
            "Like": "like",
            "Love": "love",
            "Haha": "haha",
            "Angry": "angry",
            "Wow": "wow",
            "Sad": "sad"
            }

def pullFromMongo(coll, keyID):
    search = coll.find()
    dictVar = {}
    for r in search:
        dictVar[r[keyID]] = r
    return dictVar

delay = 10