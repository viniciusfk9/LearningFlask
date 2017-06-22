import urllib2
import json

TOKEN = "86b196c832b502a89d60199450c079f373907623"
ROOT_URL = "https://api-ssl.bitly.com"
SHORTEN = "/v3/shorten?access_token={}&longUrl={}"


class BitlyHelper:
    def shorten_url(self, longurl):
        try:
            url = ROOT_URL + SHORTEN.format(TOKEN, longurl)
            response = urllib2.urlopen(url).read()
            jr = json.loads(response)

            return jr['data']['url']
        except Exception as e:
            print e
