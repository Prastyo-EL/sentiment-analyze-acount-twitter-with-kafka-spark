from flask import Flask, render_template, abort, request, jsonify,Response
import sys
from twython import Twython
import nltk
from dictionary import Dictionary
from kafka import SimpleProducer, KafkaClient, SimpleClient, KafkaProducer
import time
import argparse



APP_KEY = 'XQ2nfh0xIuU9xwaMKx3KSd89Z'
APP_SECRET = '6kdjdnFmp2G67HlDAxlgbKhnBFzVjyI0HlP3F2JktibkMJYDf3'

#def get_kafka_client():
 #  return KafkaClient(hosts='127.0.0.1:9092')

twitter = Twython(APP_KEY, APP_SECRET, oauth_version=2)
ACCESS_TOKEN = twitter.obtain_access_token()

twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)

parser = argparse.ArgumentParser(description="Scrape twitter data and put it into Kafka.")
parser.add_argument("t", nargs=1, help="topics list")
args = parser.parse_args()
topic_name = args.t[0]

app = Flask(__name__)

class SentimentScore:
    def __init__(self, positive_tweets, negative_tweets, neutral_tweets, positive_tweets1, negative_tweets1, neutral_tweets1):

        self.positive_tweets = positive_tweets
        self.negative_tweets = negative_tweets
        self.neutral_tweets = neutral_tweets
        self.positive_tweets1 = positive_tweets1
        self.negative_tweets1 = negative_tweets1
        self.neutral_tweets1 = neutral_tweets1


        self.neg = len(negative_tweets)
        self.pos = len(positive_tweets)
        self.neut = len(neutral_tweets)
        self.neg1 = len(negative_tweets1)
        self.pos1 = len(positive_tweets1)
        self.neut1 = len(neutral_tweets1)

dictionaryN = Dictionary('negative-words.txt')
dictionaryP = Dictionary('positive-words.txt')

def sentiment(tweet):
    negative_score = 0
    positive_score = 0
    #menentukan sentiment dengan nltk
    tokenizer = nltk.tokenize.TweetTokenizer()
    tweet_words = tokenizer.tokenize(tweet)
    for word in tweet_words:
        negative_score += dictionaryN.check(word)
    for word in tweet_words:
        positive_score += dictionaryP.check(word)
    if negative_score > positive_score:
        return 'negative' and 'negative1'
    elif negative_score == positive_score:
        return 'neutral' and 'neutral1'
    else:
        return 'positive' and 'positive1'

    # use dictionary to count negative frequent

def sentiment_analysis(tweets):
    negative_tweets = []
    positive_tweets = []
    neutral_tweets = []
    negative_tweets1 = []
    positive_tweets1 = []
    neutral_tweets1 = []
    #menampung tweet sentiment negative, positive dan neutral
    for tweet in tweets:
        res = sentiment(tweet['text'])
        if res == ('negative' and 'negative1'):
            negative_tweets.append(tweet['text'])
            negative_tweets1.append(tweet['text'])
        elif res == ('positive' and 'positive1'):
            positive_tweets.append(tweet['text'])
            positive_tweets1.append(tweet['text'])
        else:
            neutral_tweets.append(tweet['text'])
            neutral_tweets1.append(tweet['text'])
    return SentimentScore(positive_tweets, negative_tweets, neutral_tweets,positive_tweets1, negative_tweets1, neutral_tweets1)

@app.route("/", methods=["POST","GET"])
def root():
    global list_result,username,username1,username2,username3,username4
    if request.method == "POST":#mengirim 2 akun twitter
        username = request.form['twitter_username']
        user_timeline = twitter.get_user_timeline(screen_name=username, count = 20)
        result=sentiment_analysis(user_timeline)
        username1 = request.form['twitter_username1']
        user_timeline1 = twitter.get_user_timeline(screen_name=username1, count = 20)
        result1=sentiment_analysis(user_timeline1)
        #menampung hasil tweet ke kafka
        for tweet in user_timeline:
            try:
                client = SimpleClient("localhost:9092")
                producer = SimpleProducer(client, async=False,
                                       batch_send_every_n=10,
                                       batch_send_every_t=2)
                print(tweet['text'])
                msg = tweet['text'].encode('utf-8')
                producer.send_messages(topic_name, msg)
                # producer.send('test', key=bytes('tweet', encoding='utf-8'), value=bytes(tweet['text'],encoding='utf-8'))
                # producer.flush()
                print('publish success')
            except Exception as ex:
                print('Exception in publishing message')
                print(str(ex))
        time.sleep(30)
        for tweet in user_timeline1:
            try:
                client = SimpleClient("localhost:9092")
                producer = SimpleProducer(client, async=False,
                                       batch_send_every_n=10,
                                       batch_send_every_t=2)
                print(tweet['text'])
                msg = tweet['text'].encode('utf-8')
                producer.send_messages(topic_name, msg)
                # producer.send('test', key=bytes('tweet', encoding='utf-8'), value=bytes(tweet['text'],encoding='utf-8'))
                # producer.flush()
                print('publish success')
            except Exception as ex:
                print('Exception in publishing message')
                print(str(ex))
        time.sleep(30)
        return render_template("result.html", result=sentiment_analysis(user_timeline),result1=sentiment_analysis(user_timeline1))
    else:
        return render_template("index.html")

#update data ketika ada perubahan pada akun twitter
@app.route('/refreshData')
def refresh_graph_data():
    global list_result,username
    user_timeline = twitter.get_user_timeline(screen_name=username, count = 20)
    result=sentiment_analysis(user_timeline)
    list_result = [result.pos,result.neut,result.neg]
    # list_result = [10,10,10]
    for tweet in user_timeline:
            try:
                client = SimpleClient("localhost:9092")
                producer = SimpleProducer(client, async=False,
                                       batch_send_every_n=10,
                                       batch_send_every_t=2)
                print(tweet['text'])
                msg = tweet['text'].encode('utf-8')
                producer.send_messages(topic_name, msg)
                # producer.send('test', key=bytes('tweet', encoding='utf-8'), value=bytes(tweet['text'],encoding='utf-8'))
                # producer.flush()
                print('publish success')
            except Exception as ex:
                print('Exception in publishing message')
                print(str(ex))
    time.sleep(30)
    return jsonify(sResult=list_result)
@app.route('/refreshData1')
def refresh_graph_data1():
    global list_result1,username1
    user_timeline1 = twitter.get_user_timeline(screen_name=username1, count = 20)
    result1=sentiment_analysis(user_timeline1)
    list_result1 = [result1.pos1,result1.neut1,result1.neg1]
    for tweet in user_timeline1:
            try:
                client = SimpleClient("localhost:9092")
                producer = SimpleProducer(client, async=False,
                                       batch_send_every_n=10,
                                       batch_send_every_t=2)
                print(tweet['text'])
                msg = tweet['text'].encode('utf-8')
                producer.send_messages(topic_name, msg)
                # producer.send('test', key=bytes('tweet', encoding='utf-8'), value=bytes(tweet['text'],encoding='utf-8'))
                # producer.flush()
                print('publish success')
            except Exception as ex:
                print('Exception in publishing message')
                print(str(ex))
    time.sleep(30)
    # list_result = [10,10,10]
    return jsonify(sResult1=list_result1)


# @app.route('/topic/<list_result>')
# def get_messages(list_result):
#     #client = get_kafka_client()
#     client = KafkaClient(hosts="localhost:9092")
#     topi = client.topics[list_result]

#     producer = topi.get_sync_producer()
#     def events():
#         for i in client.topics[list_result].get_simple_consumer():
#             yield 'data:{0}\n\n'.format(i.value.decode())
#     return Response(events(), mimetype="text/event-stream")
    
# @app.route('/topic/<list_result>')
# def get_messages(list_result):
#     client = KafkaClient(hosts="localhost:9092")
#     topi = client.topics[list_result]

#     producer = topi.get_sync_producer()
#     def events():
#         count =1
#         mes = (list_result)
#         producer.produce(mes.encode('ascii'))
#         print(mes)
#     return Response(events(), mimetype="text/event-stream")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(debug=True,host='localhost', port=5002)
