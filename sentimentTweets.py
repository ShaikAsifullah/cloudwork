'''
Created on Sep 28, 2015

@author: Asif
'''
#Import the tweepy library and the required methods
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
import codecs
import en


class SentiWordNetDemoCode:
    
    def __init__(self):
        self.dictionary = {}
        
        self.proceed()
    
    def proceed(self):
                
        tempDictionary = {}
        f = open("sentiwordnet.txt","r")
        
        line_number = 0
        for lines in f.readlines():
            if(not lines):
                continue
            else:
                line_number += 1
                if(not lines.strip().startswith('#')):
                    data = lines.split("\t")
                    
                    wordtype = data[0]
                    synsetscore = float(data[2]) - float(data[3])
                    
                    #get all synset terms
                    syntermssplit = data[4].split()
                    
                    for item in syntermssplit:
                        syntermandrank = item.split('#')
                        
                        synterm = syntermandrank[0] + "#"+ wordtype
                        
                        syntermrank = int(syntermandrank[1])
                        
                        if(not tempDictionary.has_key(synterm)):
                            tempDictionary[synterm] = []
                        
                        tempDictionary[synterm].append((syntermrank,synsetscore))
            
        #go from here
        for mykeys in tempDictionary.keys():
            mylist = tempDictionary[mykeys]
            score = 0.0
            mysum = 0.0
            for each_item in mylist:
                score += (each_item[1]*1.0/each_item[0])
                mysum += 1.0/each_item[0]
            score /= mysum
            self.dictionary[mykeys] = score
        f.close()
    
    def extract(self,word,pos):
        return(self.dictionary[word+"#"+pos])
    

class TweetData:
    
    def __init__(self,tweets):
        self.myText = tweets
        #Provide Stop words file name here
        STOPWORDS_filename = "stopWords.txt"
        
        #Open the STOP WORDS file
        f = open(STOPWORDS_filename,'r')
        self.STOPWORDS = set()
        content = f.read()
        
        #Add the words to the set so that the search is faster
        for words in content.split():
            self.STOPWORDS.add(words)
        f.close()
        
    
    def getWork(self):
        positive = 0
        negative = 0
        a = SentiWordNetDemoCode();
        for lines in self.myText:
            words = lines.split()
            for word in words:
                try:
                    word = str(word)
                except:
                    continue
                if(word in self.STOPWORDS):
                    continue
                try:
                    category = self.getcategory(word)
                    if(not category):
                        continue
                    VAL = a.extract(word, category)
                    if(VAL>0):
                        positive += VAL
                    else:
                        negative -= VAL
                    
                    #print(word,category,a.extract(word, category))
                except:
                    pass
        
        print "This is positive ",positive
        print "This is negative ",negative
        print "The Total is ",positive-negative
    
    def getcategory(self,word):
        #Higher prirority for verb
        try:
            if(en.verb.present(word)):
                return("v")
        except:
            pass
        
        #Check if it is a noun
        if(en.is_noun(word)):
            return("n")
        
        #Check if it is an adjective
        elif(en.is_adjective(word)):
            return("a")
            
        else:
            return(None)
        



#Credentials for API DO NOT SHARE or MISUSE
access_token = "3263176286-pI7DTxVl4Ky7W36f121Ae73Kz6RwEoLpVWCy0de"
access_token_secret = "aevy3yNBEWgFylQs6q1xTamlyfVslfVvArrERYQkZ4L77"
consumer_key = "M3EVPa1UTbGim1tLbzPAvDg3w"
consumer_secret = "ITq5gqAybCTWFy3OK2FEKjGHs9gPcz3tSj8RV3mSvymHsH7oVr"


##SETS
crude_oil = set()
sp = set()
usd = set()
eur = set()

#Main class
class MyListener(StreamListener):
    
    def __init__(self):
        
        self.file1 = codecs.open("crude.txt", 'w+', encoding='utf8')
        self.file2 = codecs.open("usd.txt", 'w+', encoding='utf8')
        self.file3 = codecs.open("eur.txt", 'w+', encoding='utf8')
        self.file4 = codecs.open("sp.txt", 'w+', encoding='utf8')
    
    def on_data(self, Tweet):
        global crude_oil,sp,usd,eur
        Tweet = json.loads(Tweet)
        newTweet = Tweet["text"].lower()
        if "crude" in newTweet:
            crude_oil.add(newTweet)
            self.file1.write(newTweet+"\n\n")
            
        if "usd" in newTweet:
            usd.add(newTweet)
            self.file2.write(newTweet+"\n\n")
            
        if "eur" in newTweet:
            eur.add(newTweet)
            self.file3.write(newTweet+"\n\n")
            
        if "s&amp;p" in newTweet:
            sp.add(newTweet)
            self.file4.write(newTweet+"\n\n")
        
        #print(len(crude_oil),len(usd),len(eur),len(sp))
        if(len(crude_oil) > 2 and len(usd) > 2 and len(sp) > 2):
            for tweets_data in [crude_oil,sp,usd,eur]:
                
                t = TweetData(tweets_data)
                t.getWork()
            quit()
        return True

    def on_error(self, status):
        print status


if __name__ == '__main__':

    
    mylistener = MyListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, mylistener)
    stream.filter(track=["S&amp;P 500","crude oil","#eur","#usd"])
    
    