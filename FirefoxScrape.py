from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import pymongo
import time
from config import EMAIL, GEN_PASS
from datetime import datetime, timedelta

def initialize():
    print(f"Run started at {startTime}")
#    option = webdriver.ChromeOptions()
#    option.add_argument("--incognito")
#    option.add_argument("--window-size=1440,800")
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.privatebrowsing.autostart", True)
    browser = webdriver.Firefox(executable_path='geckodriver.exe', firefox_profile=profile)
    return browser

def fbLogin(driver):
    driver.get('https://www.facebook.com/')
    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, "email")))
    driver.find_element_by_id('email').send_keys(EMAIL)
    passField = driver.find_element_by_id('pass')
    passField.send_keys(GEN_PASS)
    passField.send_keys(Keys.RETURN)
    time.sleep(2)

def retrievePosts():
    results = browser.find_elements_by_xpath('//div[@role="article"]')
    for res in results:
        try:
            articleLink = res.find_element_by_xpath('./div[2]/div[2]/a[1]').get_attribute('href')
            articleLinks.append(articleLink)
        except:
            continue
    return articleLinks

def commentScrape():
    browser.get(link)
    WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.ID, "m_story_permalink_view")))
    timeout = datetime.now() + timedelta(minutes=10)
    try:
        while browser.find_element_by_id(f'see_next_{postID}') and datetime.now() < timeout:
            commentsFields()
            browser.find_element_by_id(f'see_next_{postID}').find_element_by_xpath('./a').click()
            time.sleep(1)
    except NoSuchElementException:
        try:
            commentsFields()
        except:
            pass

def commentsFields():
    container = browser.find_element_by_id('m_story_permalink_view')
    comments = container.find_elements_by_xpath('./div[2]/div/div[5]/div')
    for comment in comments:
        try:
            commentID = comment.get_attribute('id')
            if commentID != f'see_next_{postID}' and commentID != f'see_prev_{postID}':
                commentText = comment.find_element_by_xpath('./div/div[1]').text
                try:
                    authorElem = comment.find_element_by_xpath('./div/h3/a')
                except Exception as e:
                    print(repr(e))
                    authorElem = ""
                try:
                    author = authorElem.text
                    profile = authorElem.get_attribute('href').split('?')[0]
                except Exception as e:
                    print(repr(e))
                    author = ''
                    profile = ''
                try:
                    repliesLink = comment.find_element_by_id(f'comment_replies_more_1:{postID}_{commentID}').find_element_by_xpath('./div[2]/a').get_attribute('href')
                    gatherReplies(repliesLink, commentID)
                except Exception as e:
                    print(repr(e))
                    try:
                        repliesLink = comment.find_element_by_id(f'comment_replies_more_1:{postID}_{commentID}').find_element_by_xpath('./div/a').get_attribute('href')
                        gatherReplies(repliesLink, commentID)
                    except Exception as e:
                        print(repr(e))
                        repliesLink = ''
                try:
                    reactionsLinkElem = comment.find_element_by_xpath('./div/div[3]/span[1]/span/a[1]')
                    if 'Like' not in reactionsLinkElem.text:
                        reactionsLink = comment.find_element_by_xpath('./div/div[3]/span[1]/span/a[1]').get_attribute('href')
                        reactions = gatherReactions(reactionsLink, commentID)
                    else:
                        reactions = []
                        reactionsLink = ''
                except Exception as e:
                    print(repr(e))
                    reactionsLink = ''
                    reactions = []
                commentsStorage[commentID] = {
                    "article": link,
                    "articleID": postID,
                    "commentID": commentID,
                    "text": commentText,
                    "reactions": {key:int(value) for (key, value) in reactions},
                    "replies": repliesLink,
                    "reactionsLink": reactionsLink,
                    "author": author,
                    "profile": profile
                    }
                total = sum([int(value) for (key, value) in reactions])
                commentsStorage[commentID]["reactions"]["total"] = total
                search = commentsCollection.find({"commentID":commentsStorage[commentID]['commentID']})
                if len([r for r in search]) == 0:
                    commentsCollection.insert_one(commentsStorage[commentID])
                else:
                    commentsCollection.update_one({"commentID":commentsStorage[commentID]['commentID']},
                                                   {'$set': commentsStorage[commentID]})
        except StaleElementReferenceException:
            continue

def gatherReactions(reactionsLink, commentID, replyID=''):
    reactionsList = []
    browser3.get(reactionsLink)
    WebDriverWait(browser3, delay).until(EC.presence_of_element_located((By.CLASS_NAME, "z")))
    reactionCounts = browser3.find_element_by_class_name('z').find_elements_by_tag_name('a')
    for reaction in reactionCounts:
        reactionLink = reaction.get_attribute('href')
        if 'reaction_type' in reactionLink:
            val = reactionLink.split('reaction_type=')[1].split('&')[0]
            reactType = reactionsDict[val]
            count = reactionLink.split('total_count=')[1].split('&')[0]
            reactionsList.append((reactType, count))
    repeat = True
    try:
        while repeat:
            gatherReactionAuthors(browser3, replyID, commentID)
            time.sleep(1)
        print(reactionsList)
        return reactionsList
    except:
        return reactionsList

def gatherReactionAuthors(browser3, replyID, commentID):
    reacts = browser3.find_element_by_tag_name('ul').find_elements_by_tag_name("li")
    if len(reacts) < 2:
        print([x for x in reacts])
    repeat = False
    for react in reacts:
        print(react.text.encode('ascii', 'ignore'))
        if 'See More' in react.text:
            repeat = True
            react.find_element_by_tag_name('a').click()
            break
        reactImages = react.find_elements_by_tag_name('img')
        for reactImage in reactImages:
            reactImg = reactImage.get_attribute('alt')
            if reactImg in reactionsDict:
                reactResponse = reactionsDict[reactImg]
        reactAuthorProfile = react.find_element_by_xpath('./table/tbody/tr/td/table/tbody/tr/td[3]/div/h3[1]/a').get_attribute('href')
        splitProfile = reactAuthorProfile.split('facebook.com/')[1].split('/')[0]
        concatString = f"{commentID}{replyID}{splitProfile}"
        reactionsStorage[concatString] = {
            "postID": postID,
            "reactID": concatString,
            "reaction": reactResponse,
            "comment": commentID,
            "reply": replyID,
            "author": reactAuthorProfile
        }
        search = reactionsCollection.find({"reactID":reactionsStorage[concatString]['reactID']})
        if len([r for r in search]) == 0:
            reactionsCollection.insert_one(reactionsStorage[concatString])
        else:
            repliesCollection.update_one({"reactID":reactionsStorage[concatString]['reactID']},
                                                   {'$set': repliesStorage[concatString]})

def gatherReplies(repliesLink, commentID):
    browser2.get(repliesLink)
    WebDriverWait(browser2, delay).until(EC.presence_of_element_located((By.ID, commentID)))
    try:
        while browser2.find_element_by_xpath(f'//div[@id = {commentID}]/following-sibling::div').find_element_by_xpath('./div'):
            repliesFields(commentID)
            browser2.find_element_by_xpath(f'//div[@id = {commentID}]/following-sibling::div').find_element_by_xpath('./div/a').click()
            time.sleep(1)
    except NoSuchElementException:
        try:
            print("NoSuchElementException")
            repliesFields(commentID)
        except:
            print("Failed on gathering replies")

def repliesFields(commentID):
    responses = browser2.find_element_by_xpath(f'//div[@id = {commentID}]/following-sibling::div').find_elements_by_xpath('./div')
    for response in responses:
        replyID = response.get_attribute('id')
        if replyID == f"comment_replies_more_2:{postID}_{commentID}":
            response.find_element_by_xpath('./a').click()
            time.sleep(1)
            repliesFields(commentID)
        if replyID != f"comment_replies_more_1:{postID}_{commentID}":
            replyText = response.find_element_by_xpath('./div/div[1]').text
            replyAuthorElem = response.find_element_by_tag_name('h3').find_element_by_tag_name('a')
            replyAuthor = replyAuthorElem.text
            replyAuthorProfile = replyAuthorElem.get_attribute('href').split('?')[0]
            reactionsLinkElem = response.find_element_by_id(f'like_{postID}_{replyID}').find_element_by_xpath('./span/a[1]')
            if 'Like' not in reactionsLinkElem.text:
                replyReactionsLink = reactionsLinkElem.get_attribute('href')
                replyReactions = gatherReactions(replyReactionsLink, commentID, replyID)
            else:
                replyReactions = []
            repliesStorage[replyID] = {
                    "postID": postID,
                    "commentID": commentID,
                    "replyID": replyID,
                    "text": replyText,
                    "reactions": {key:int(value) for (key, value) in replyReactions},
                    "author": replyAuthor,
                    "profile": replyAuthorProfile
                    }
            total = sum([int(value) for (key, value) in replyReactions])
            repliesStorage[replyID]["reactions"]["total"] = total
            search = repliesCollection.find({"replyID":repliesStorage[replyID]['replyID']})
            if len([r for r in search]) == 0:
                repliesCollection.insert_one(repliesStorage[replyID])
            else:
                repliesCollection.update_one({"replyID":repliesStorage[replyID]['replyID']},
                                                       {'$set': repliesStorage[replyID]})

def pullFromMongo(coll, keyID):
    search = coll.find()
    dictVar = {}
    for r in search:
        dictVar[r[keyID]] = r
    return dictVar

if __name__ == '__main__':
    startTime = datetime.now()
    conn = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(conn)
    db = client.dt_posts
    commentsCollection = db.comments
    repliesCollection = db.replies
    reactionsCollection = db.reactions

    commentsStorage, repliesStorage, reactionsStorage = pullFromMongo(commentsCollection, 'commentID'), pullFromMongo(repliesCollection, 'commentID'), pullFromMongo(reactionsCollection, 'reactID')
    delay = 10
    articleLinks, articles = [], []
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

    browser = initialize()
    browser2 = initialize()
    browser3 = initialize()
    fbLogin(browser)
    fbLogin(browser2)
    fbLogin(browser3)

    browser.get('https://mobile.facebook.com/pg/DonaldTrump/posts/')
    WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.ID, "structured_composer_async_container")))
    for i in range(5):
        articles.extend(retrievePosts())
        browser.find_element_by_id('structured_composer_async_container').find_element_by_xpath('./div[2]/a').click()
        time.sleep(2)

    for link in articleLinks:
        postID = link.split('story_fbid=')[1].split('&')[0]
        commentScrape()
    print(f"Run completed at {datetime.now()}")
    print(f"Elapsed time: {datetime.now() - startTime}")