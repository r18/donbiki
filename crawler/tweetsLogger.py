#coding: UTF-8
from rauth import OAuth1Service
import urllib2
import sqlite3
import daemon
import time
import datetime
import requests
import ConfigParser

try:
    read_input = raw_input
except NameError:
    read_input = input
 
con = ""
def getConfig(service):
    configFile = ConfigParser.SafeConfigParser()
    configFile.read("./config.ini")
    conf = {}
    conf["consumer_key"] = configFile.get(service,"consumer_key")
    conf["consumer_secret"] = configFile.get(service,"consumer_secret")
    conf["session_key"] = configFile.get(service,"session_key")
    conf["session_secret"] = configFile.get(service,"session_secret")
    return conf

def auth(conf):
    twitter = OAuth1Service(
        name='twitter',
        consumer_key=unicode(conf["consumer_key"]),
        consumer_secret=unicode(conf["consumer_secret"]),
        request_token_url='https://api.twitter.com/oauth/request_token',
        access_token_url='https://api.twitter.com/oauth/access_token',
        authorize_url='https://api.twitter.com/oauth/authorize',
        base_url='https://api.twitter.com/1.1/')
   
    session = twitter.get_session((
            unicode(conf["session_key"]),
            unicode(conf["session_secret"])))
    return session

def search(s):
    params = {'q': "%22%e3%83%89%e3%83%b3%e5%bc%95%e3%81%8d%2ecom%22", 
              'count': 100,
              'result_type':'recent'} # 10 tweets
    while True:
        try:
            r = s.get('search/tweets.json', params=params, verify=True)
            break
        except requests.exceptions.ConnectionError:            
            print "connection Error retry after 300 secs..."
            time.sleep(300)
            print "retring to get Tweets..."

    tweets = r.json()['statuses']
    print "get " + str(len(tweets)) + " tweets"   
    for tweet in tweets:
        rep_id = tweet['id']
        turn_id = tweet['in_reply_to_status_id']
        if rep_id != None:
            dbTweests = getTableFromDB()
            if hasDBTurnedTweet(dbTweests,turn_id):
                pairs = hasDBFirstReply(dbTweests,rep_id)
                if pairs != []:
                    saveFirstReply(s,tweet,pairs)
            else :
                saveDonbiki(s,tweet,"","")
                
            
def getTweet(s,tid):
    params = {'id':tid}
    r = s.get('statuses/show.json',params = params, verify=True)
    tweet = r.json()
    showTweet(tweet)
    return tweet

def saveFirstReply(s,tweet,pairs):
    res = getOEmbed(s,tweet['id_str'],True)
    if res != u'error' and res != u'errors':
        query = "update donbikiTweets set repIds = " +\
               pairs[0] +"," + tweet['id_str'] + ", repOembeds = " +\
                pairs[1] + "," + urllib2.quote(res) +\
                "where id = " +str(tweet['in_reply_to_status_id'])
        con.execute(query)
        print "update first reply : id = " + tweet['id_str']

def hasDBTurnedTweet(c,id):
    for row in c:
        if row[0] == id:
            return True
    return False

def hasDBFirstReply(c,id):
    pairs = []
    for row in c:
        ids = row[2].split(",")
        for i in ids:
            if i == id:
                pairs[0] = row[2]
                pairs[1] = row[3]
                return paris
    return [] 

def getTableFromDB():
    query = "select * from donbikiTweets"
    c = con.execute(query).fetchall()
    return c

def saveDonbiki(s,tweet,ids,oembeds):
    rep_emb = getOEmbed(s,tweet['id_str'],True)
    turn_emb= getOEmbed(s,tweet['in_reply_to_status_id'],False)
    if turn_emb != u'error' and rep_emb != u'error':
        query = "insert into donbikiTweets(id,oembed,created,repIds,repOembeds) values(" +\
        str(tweet[u'in_reply_to_status_id']) + ",\"" +\
        urllib2.quote(turn_emb) + "\",\""+\
        tweet[u'created_at'] + "\"," +\
        tweet['id_str'] + ",\"" +\
        urllib2.quote(rep_emb)  +\
        "\")"
            #query = "update donbikiTweets set turned = " + str(ct) +\
            #        " where id = " + tweet['id_str']
        con.execute(query)
        print "update turned tweet : id =" + str(tweet[u'in_reply_to_status_id'])
        return True
    else:
        return False
       

def getOEmbed(s,tid,th):
    url = "https://twitter.com/#!/twitter/status/"+str(tid)
    params = {'id':tid , 'hide_thread':th,'omit_script':'true'}
    r = s.get("statuses/oembed.json",params = params,verify=True).json()
    if not r.has_key(u'error') and not r.has_key(u'errors'):
        st = str(r[u'html'].split(","))
        return st[3:len(st)-5]
        
    else:
        return u"error"

def showTweet(r):
    print(u'ドン引きされたTweet: @{0} - {1}').format(r['user']['screen_name'],r['text'])

if __name__ == '__main__':
    conf = getConfig("twitter")
    sess = auth(conf)
    while True:
        con = sqlite3.connect("../htdocs/tweets.db",isolation_level=None)
        print datetime.datetime.today().strftime("[%Y-%m-%d %H:%M:%S]") + " crawling..."
        search(sess)
        print datetime.datetime.today().strftime("[%Y-%m-%d %H:%M:%S]") + "finished crawling"
        con.close()
        time.sleep(180)
