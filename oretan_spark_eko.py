from __future__ import print_function
import argparse
import json
import re
import nltk
# from stop_words import get_stop_words
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from dictionary import Dictionary

# class SentimentScore:
#     def __init__(self, positive_tweets, negative_tweets, neutral_tweets, positive_tweets1, negative_tweets1, neutral_tweets1):

#         self.positive_tweets = positive_tweets
#         self.negative_tweets = negative_tweets
#         self.neutral_tweets = neutral_tweets
#         self.positive_tweets1 = positive_tweets1
#         self.negative_tweets1 = negative_tweets1
#         self.neutral_tweets1 = neutral_tweets1


#         self.neg = len(negative_tweets)
#         self.pos = len(positive_tweets)
#         self.neut = len(neutral_tweets)
#         self.neg1 = len(negative_tweets1)
#         self.pos1 = len(positive_tweets1)
#         self.neut1 = len(neutral_tweets1)

dictionaryN = Dictionary('negative-words.txt')
dictionaryP = Dictionary('positive-words.txt')

def sentiment(tweet):
    negative_score = 0
    positive_score = 0
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

# def sentiment_analysis(tweets):
#     negative_tweets = []
#     positive_tweets = []
#     neutral_tweets = []
#     negative_tweets1 = []
#     positive_tweets1 = []
#     neutral_tweets1 = []

#     for tweet in tweets:
#         res = sentiment(tweet['text'])
#         if res == ('negative' and 'negative1'):
#             negative_tweets.append(tweet['text'])
#             negative_tweets1.append(tweet['text'])
#         elif res == 'positive' and 'positive1':
#             positive_tweets.append(tweet['text'])
#             positive_tweets1.append(tweet['text'])
#         else:
#             neutral_tweets.append(tweet['text'])
#             neutral_tweets1.append(tweet['text'])
#     return SentimentScore(positive_tweets, negative_tweets, neutral_tweets,positive_tweets1, negative_tweets1, neutral_tweets1)

def main():
    #streamingkan hasil sentiment ke spark
    parser = argparse.ArgumentParser(description="Gets twitter data from Kafka and work with it.")
    parser.add_argument("broker", nargs=1, help="broker name")
    parser.add_argument("topics", nargs="+", help="topics list")
    parser.add_argument("batch", nargs=1, type=int, help="Batch duration for StreamingContext")
    args = parser.parse_args()

    broker = args.broker[0]
    topics = args.topics
    batch_duration = args.batch[0]

    print(broker, topics, type(batch_duration))

    conf = SparkConf()
    conf.setAppName("TwitterStreamApp")

    sc = SparkContext(conf=conf)
    sc.setLogLevel("ERROR")

    ssc = StreamingContext(sc, batch_duration)

    # brokers, topics = 'localhost:9092', 'test2'
    kvs = KafkaUtils.createDirectStream(ssc, topics, {"metadata.broker.list": broker})

    # text_pattern = r'[А-ЯЁа-яё]*'

    lines = kvs.map(lambda x: x[1])
    ssc.checkpoint("./checkpoint-tweet")

    lines.count().map(lambda x: 'Tweets in this batch: %s' % x).pprint()

    # running_counts = lines.flatMap(lambda line: line.split(" ")) \
    #     .map(lambda word: (word, 1)) \
    #     .updateStateByKey(update_func).transform(lambda rdd: rdd.sortBy(lambda x: x[1], False))
    # running_counts.count().map(lambda x: 'Tweets at all: %s' % x).pprint()
    hasil_sentimen = lines.map(lambda line: sentiment(line))
    sentimen_to_cnt = hasil_sentimen.map(lambda x: (x, 1))
    sentimen_cnt = sentimen_to_cnt.reduceByKey(lambda a,b : a+b)
    sentimen_cnt.pprint()

    ssc.start()
    ssc.awaitTermination()


def update_func(new_values, last_sum):
    return sum(new_values) + (last_sum or 0)


if __name__ == "__main__":
    main()

# spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.1.0 oretan_spark_eko.py localhost:9092 tweet 5