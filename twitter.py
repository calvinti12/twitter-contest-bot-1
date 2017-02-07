from TwitterAPI import TwitterAPI


class Twitter(object):

    def __init__(self, consumer_key, consumer_secret, access_token_key, access_token_secret ):
        print 'Twitter'
        self.api = TwitterAPI(consumer_key, consumer_secret,
                         access_token_key, access_token_secret)