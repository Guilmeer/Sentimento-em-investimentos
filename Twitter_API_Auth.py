import tweepy

class Twitterapi:
    #Tokens de acesso
    consumer_key= '#####'
    consumer_secret= '#####'
    access_token='#####'
    access_token_secret='#####'

    #Autenticando
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth,wait_on_rate_limit=True)
    def get_api(self):
        return self.api
