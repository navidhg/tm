import flask
import requests
import twitter as twitter_wrapper
from datetime import datetime, timedelta
from time import mktime
from flask import Flask, jsonify, redirect, request, session, url_for
from flask_cors import CORS, cross_origin
from flask_oauthlib.client import OAuth

app = Flask(__name__, static_url_path='/static')
app.secret_key = "my secret key"
CORS(app)

myConsumerKey = "<insert here>"
myConsumerSecret = "<insert here>"
myAccessTokenKey = "<insert here>"
myAccessTokenSecret = "<insert here>"

# OAuth
oauth = OAuth()
twitter = oauth.remote_app('twitter',
    base_url='https://api.twitter.com/1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    consumer_key=myConsumerKey,
    consumer_secret=myConsumerSecret
)

@twitter.tokengetter
def twitterGetToken(token=None):
	return session.get("twitterToken")

@app.route("/")
def home():
	return app.send_static_file('index.html')

@app.route('/<path:path>')
def static_proxy(path):
  return app.send_static_file(path)

@app.route("/login")
def login():
	return twitter.authorize(callback=url_for('oauth_authorized', next=None))

@app.route('/oauth-authorized')
def oauth_authorized():
    next_url = url_for('home') 
    resp = twitter.authorized_response()
    if resp is None:
    	print "ERROR LOGGING IN"
        return redirect(next_url)

    session['twitterToken'] = (resp['oauth_token'], resp['oauth_token_secret'] )
    session['twitter_user'] = resp['screen_name']
    session.modified = True
    
    print "LOGGED IN", "key", resp['oauth_token'], "secret", resp['oauth_token_secret'], resp['screen_name']
    return redirect(next_url)

@app.before_request
def before_request():
    if "twitterToken" in session:
    	print "SETTING UP TWITTER WRAPPER"
        flask.g.api = getTwitterAPI()
    else:
    	print "COULD NOT FIND TWITTER TOKEN IN SESSION"

def getTwitterAPI():
	twitterToken = twitterGetToken()
	accessTokenKey = twitterToken[0]
	accessTokenSecret = twitterToken[1]

	api = twitter_wrapper.Api(
		consumer_key=myConsumerKey, 
		consumer_secret=myConsumerSecret, 
		access_token_key=accessTokenKey, 
		access_token_secret=accessTokenSecret
	)
	print "VERIFYING CREDENTIALS", api.VerifyCredentials()
	return api

@app.route("/friends")
def friendsNotFollowers():
	friends = flask.g.api.GetFriends()
	friendIDs = map(lambda x: x.id, friends)
	friendIDMap = {}
	for friend in friends:
		friendIDMap[friend.id] = friend
	followerIDs = flask.g.api.GetFollowerIDs()
	idDiff = list(set(friendIDs) - set(followerIDs))
	userDiff = []
	for userID in idDiff:
		userDiff.append(friendIDMap[userID].screen_name)
	return jsonify(userDiff)

def getTweetThreshold():
	earliestTweet = datetime.today() - timedelta(days=30)
	return int(mktime(earliestTweet.timetuple()))

@app.route("/recent")
def getRecentTweets():
	timeline = flask.g.api.GetUserTimeline()
	threshold = getTweetThreshold()
	recent = []
	for t in timeline:
		if t.created_at_in_seconds < threshold:
			break
		else:
			recent.append({"time": t.created_at, "tweet": t.text})
	return jsonify(recent)
