import tweepy
import os
import math
import datetime
import re

class TimeLimitExceedError(Exception):
    def __init__(self, message):
        self.message = message

# n: 素数かどうか判定されるもの
# 素数でなければFalse, 素数の可能性があればTrue
def Miller_Rabin_test(n, a):
    if n == 2:
        return True
    if n < 2 or n % 2 == 0:
        return False
    d = n - 1
    s = 0
    while d & 1 == 0:
        d >>= 1
        s += 1
    if pow(a, d, n) == 1:
        return True
    r = 1
    for i in range(s):
        if pow(a, d * r, n) == n - 1:
            return True
        r <<= 1
    return False

#ミラーラビン素数判定法を用いた素数判定
def is_prime(n):
    result = True
    start_time = datetime.datetime.now()
    for a in range(2, min(n, 2 * int(math.log(n) ** 2) + 1)):
        now_time = datetime.datetime.now()
        if(now_time - start_time).seconds >= 5:
            raise TimeLimitExceedError("TLE")
        result = result and Miller_Rabin_test(n, a)
        if not result:
            return result
    return result

def is_alpha(char):
    c = ord(char)
    if ord("A") <= c <= ord("Z") or ord("a") <= c <= ord("z"):
        return True
    return False

def is_digit(char):
    c = ord(char)
    if ord("0") <= c <= ord("9"):
        return True
    return False

# TwitterのIDとして使える文字かどうか
def is_availabe_char(char):
    if is_alpha(char) or is_digit(char) or char == "_":
        return True
    return False

# ツイートの中から数字列を抽出する。なかった場合は空文字列を返す。
def find_number(text):
    i = 0
    while i < len(text):
        if text[i] == "@":
            i += 1
            while i < len(text) and is_availabe_char(text[i]):
                i += 1
            i += 1
            continue
        if i < len(text) and is_digit(text[i]):
            number_begin_index = i
            while i < len(text) and is_digit(text[i]):
                i += 1
            return text[number_begin_index:i]
        i += 1
    return ""

# テストツイートのメッセージ
def test_message():
    date = datetime.datetime.now() + datetime.timedelta(hours=8, minutes=50)
    return "This is a test tweet({}/{}/{} {}:{}:{})".format(date.year, date.month, date.day, date.hour, date.minute, date.second)

# 今日が素数の日かどうかのメッセージ
# date_todayは今日の日付
def prime_number_day_message(date_today):
    #　今日の年月日を記録
    year = date_today.year
    month = date_today.month
    day = date_today.day
    #　nは8桁の整数で、n=YYYYMMDD
    n = year * 10000 + month * 100 + day
    if is_prime(n):
        return "Today({}/{}/{}) is a prime day!".format(year, month, day)
    else:
        return "Today({}/{}/{}) is not a prime day :(".format(year, month, day)

# リプライで送られた整数が素数かどうかのメッセージ
def prime_judge_message(n):
    if n == 57:
        return "57 is the Grothendieck Prime!"
    is_prime_flag = False
    try:
        is_prime_flag = is_prime(n)
    except TimeLimitExceedError as e:
        # 時間がかかり過ぎた場合の処理
        return "Oops! This number is too big to judge."
    if is_prime_flag:
        return "{} is a prime number!".format(n)
    else:
        return "{} is not a prime number :(".format(n)

# 一日一回、今日が素数の日かどうかをつぶやく
def tweet_prime_day(api):
    # 0:10(JST)にツイートするために、UTC+08:50としている
    date_today = datetime.datetime.now() + datetime.timedelta(hours=8, minutes=50)
    day = date_today.day
    last_tweet_day = 0
    # 1日1回だけツイートするための処理
    with open("last_tweet_day.txt") as f:
        last_tweet_day = int(f.read())
    if day == last_tweet_day:
        return
    try:
        # ツイート
        api.update_status(prime_number_day_message(date_today))
    except tweepy.error.TweepError as e:
        # エラーログ
        with open("log.txt", "a") as f:
            f.write("{} {}".format(datetime.datetime.today(), e))
    else:
        with open("last_tweet_day.txt", "w") as f:
            f.write(str(day))

# botのテストツイートをする
def tweet_test(api):
    api.update_status(test_message())

# リプライで来た数について、素数かどうかをリプライで伝える
def reply_to_tweets(api):
    # 最後に返信したリプライのIDを取得
    since = int(open("since_id.txt").read())
    mentions = api.mentions_timeline(since_id=since)
    for mention in mentions:
        since = max(since, mention.id)
        # bot自身の返信を無視
        if mention.source == "prime number bot":
            continue
        str_num = find_number(mention.text)
        if str_num == "":
            continue
        n = int(str_num)
        try:
            api.update_status("@" + mention.user.screen_name + " " + prime_judge_message(n) + " (ID: " + str(mention.id)[-4:] + ")", mention.id)
        except tweepy.error.TweepError as e:
            # エラーログ
            with open("log.txt", "a") as f:
                f.write("{} {}".format(datetime.datetime.today(), e))
    with open("since_id.txt", "w") as f:
        f.write(str(since))
