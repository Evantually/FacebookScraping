import pandas as pd
from pprint import pprint
from vaderSentiment import vaderSentiment
import pymongo
from collections import defaultdict

def sentiment():
    
    commentsStorage = pd.read_csv('DTFBComments.csv', encoding='utf-8', index_col=0).transpose().to_dict()
    for comment in commentsStorage:
        print(commentsStorage[comment]['reactions'])
        evalStr = commentsStorage[comment]['text']
        try:
            commentsStorage[comment]['score'] = analyzer.polarity_scores(evalStr)['compound']
        except:
            commentsStorage[comment]['score'] = 0
    df = pd.DataFrame(commentsStorage).transpose()
    print(df['text'].value_counts())
    results = df['authorProfile'].loc[df['text'] == '']
    for res in results:
        print(res)
        
def pullFromMongo(coll):
    search = coll.find()
    dictVar = {}
    for r in search:
        dictVar[r['commentID']] = r
    return dictVar

def popularWords():
    sentence_scores = defaultdict(float)
    word_scores = defaultdict(float)
    word_counts = defaultdict(int)
    five_words = defaultdict(float)
    five_counts = defaultdict(int)
    four_words = defaultdict(float)
    four_counts = defaultdict(int)
    three_words = defaultdict(float)
    three_counts = defaultdict(int)
    two_words = defaultdict(float)
    two_counts = defaultdict(int)
    for comment in df.text:
        sentences = comment.split(".")
        words = comment.split(" ")
        wordsLen = len(words)
        for index, sentence in enumerate(sentences):
            sentence_scores[index] = analyzer.polarity_scores(sentence)['compound']
        for index, word in enumerate(words):
            word_scores[word] = analyzer.polarity_scores(word)['compound']
            word_counts[word] += 1
            if index < wordsLen - 2:
                len2words = words[index:index+2]
                twoStr = " ".join(len2words)
                two_words[twoStr] = analyzer.polarity_scores(twoStr)['compound']
                two_counts[twoStr] += 1
                if index < wordsLen - 3:
                    len3words = words[index:index+3]
                    threeStr = " ".join(len3words)
                    three_words[threeStr] = analyzer.polarity_scores(threeStr)['compound']
                    three_counts[threeStr] += 1
                    if index < wordsLen - 4:
                        len4words = words[index:index+4]
                        fourStr = " ".join(len4words)
                        four_words[fourStr] = analyzer.polarity_scores(fourStr)['compound']
                        four_counts[fourStr] += 1
                        if index < wordsLen - 5:
                            len5words = words[index:index+5]
                            fiveStr = " ".join(len5words)
                            five_words[fiveStr] = analyzer.polarity_scores(fiveStr)['compound']
                            five_counts[fiveStr] += 1
    var = sorted(word_scores, key=word_scores.get, reverse=False)[:25]
    for v in var:
        pprint(f"{v} : {word_scores[v]}")
    var = sorted(word_counts, key=word_counts.get, reverse=True)[:25]
    for v in var:
        pprint(f"{v} : {word_counts[v]}")
    var = sorted(five_words, key=five_words.get, reverse=False)[:25]
    for v in var:
        pprint(f"{v} : {five_words[v]}")
    var = sorted(four_words, key=four_words.get, reverse=False)[:25]
    for v in var:
        pprint(f"{v} : {four_words[v]}")
    var = sorted(three_words, key=three_words.get, reverse=False)[:25]
    for v in var:
        pprint(f"{v} : {three_words[v]}")
    var = sorted(two_words, key=two_words.get, reverse=False)[:25]
    for v in var:
        pprint(f"{v} : {two_words[v]}")
    var = sorted(five_counts, key=five_counts.get, reverse=True)[:25]
    for v in var:
        pprint(f"{v} : {five_counts[v]}")
    var = sorted(four_counts, key=four_counts.get, reverse=True)[:25]
    for v in var:
        pprint(f"{v} : {four_counts[v]}")
    var = sorted(three_counts, key=three_counts.get, reverse=True)[:25]
    for v in var:
        pprint(f"{v} : {three_counts[v]}")
    var = sorted(two_counts, key=two_counts.get, reverse=True)[:25]
    for v in var:
        pprint(f"{v} : {two_counts[v]}")

def namePrints():
    print(df['author'].value_counts())
#    results = df['authorProfile'].loc[df['text'] == '']
#    for res in results:
#        print(res)

analyzer = vaderSentiment.SentimentIntensityAnalyzer()
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)
db = client.dt_posts
commentsCollection = db.comments
comments = pullFromMongo(commentsCollection)
df = pd.DataFrame(comments).transpose()
#popularWords()
namePrints()

#res = commentsCollection.find({"})
#pprint([r for r in res])