from flask import Flask, render_template
from flask_pymongo import PyMongo
import FirefoxScrape
from random import randint

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/dt_posts"
mongo = PyMongo(app)

@app.route("/")
def index():
    records = mongo.db.comments.count()
    indexID = randint(0,records)
    comment = mongo.db.comments.find()[indexID]
    return render_template("index.html", comment=comment)


@app.route("/scrape")
def scrape():
    comments = mongo.db.comments
    comment_data = FirefoxScrape.start()
    return "Scraping Successful!"


if __name__ == "__main__":
    app.run()