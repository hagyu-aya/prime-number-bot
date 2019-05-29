from apscheduler.schedulers.blocking import BlockingScheduler
import tweet
import tweepy
import os

twische = BlockingScheduler()

@twische.scheduled_job('interval', minutes=1)
def timed_job():
    auth = tweepy.OAuthHandler(os.environ["CONSUMER_KEY"], os.environ["CONSUMER_SECRET"])
    auth.set_access_token(os.environ["ACCESS_TOKEN"], os.environ["ACCESS_TOKEN_SECRET"])
    api = tweepy.API(auth)
    tweet.reply_to_tweets(api)
    tweet.tweet_prime_day(api)

if __name__ == "__main__":
    twische.start()