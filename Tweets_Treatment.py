import tweepy
from textblob import TextBlob
from unidecode import unidecode
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from string import punctuation
from textblob.classifiers import NaiveBayesClassifier
import pandas as pd

def Get_tweets(api, pesquisa, quantidade, decode = True):
    '''Retorna uma lista de tweets em lista, pela string pesquisa e pela integer quantidade'''
    tweetlist = []
    for tweet in tweepy.Cursor(api.search,q=pesquisa, lang="pt", tweet_mode='extended').items(quantidade): #, result_type='popular', since = '2020-02-27'
        #Texto do Tweet

        if 'retweeted_status' in tweet._json:
            if decode == True: textPT = unidecode(tweet._json['retweeted_status']['full_text'])
        else:
            if decode == True: textPT = unidecode(tweet.full_text)

        if textPT not in [item[1] for item in tweetlist]:
            tweetlist.append(['@' + tweet.user.screen_name, textPT])
         
    return tweetlist
    

def Tokenizer(tweets):
    '''Usado nos Tweets. Quebra o texto em palavras para tokenização e remove stopwords'''
    newtweets = []
    for texto in tweets:    
        texto =  texto.replace('.', ' ')
        palavras = word_tokenize(texto.lower())
        stopwordS = list(stopwords.words('portuguese') + list(punctuation))
        stopwordS.append('so')
        palavras_sem_stopwords = [palavra for palavra in palavras if palavra not in stopwordS]
        newtweets.append(' '.join(palavras_sem_stopwords))
    return newtweets

def xlsx ():
    '''Realiza leitura da base de dados'''
    arquivoTreino = './baseParaTreino.xlsx'
    df = pd.read_excel(arquivoTreino)
    return df

def listTokenizer(lista):
    '''Usado na lista de frases da base de treino. Quebra o texto em palavras para tokenização e remove stopwords'''
    newlista = []
    for texto in lista:    
        texto[0] =  texto[0].replace('.', ' ')
        palavras = word_tokenize(texto[0].lower())
        stopwordS = list(stopwords.words('portuguese') + list(punctuation))
        stopwordS.append('so')
        palavras_sem_stopwords = [palavra for palavra in palavras if palavra not in stopwordS]
        newlista.append([' '.join(palavras_sem_stopwords), texto[1]])
    return newlista

def sentBayes (df, frases):
    '''
    Separa os pos e neg. Tokeniza.
    Gera nova lista com os valores.
    '''
    listneg = df[df['sent'].isin(['neg'])].values.tolist()
    listpos = df[df['sent'].isin(['pos'])].values.tolist()
    listpos = listTokenizer(listpos)
    listneg = listTokenizer(listneg)
    
    listtotal = []
    for item in listpos:
        listtotal.append(item)
    for item in listneg:
        listtotal.append(item)
    '''
    Realiza o treino
    Tenta classificar os tweets
    '''
    cl = NaiveBayesClassifier(listtotal)
    senttotal = []
    for frase in frases:
        sentvalue = [cl.classify(frase)]
        prob_dist = cl.prob_classify(frase)
        prob_pos = round(prob_dist.prob("pos"), 2)
        prob_neg = round(prob_dist.prob("neg"), 2)
        
        if prob_neg < prob_pos:
            if prob_pos - prob_neg > 0.15:
                sentvalue.append(prob_pos)
                sentvalue.append(prob_neg)
            else:
                sentvalue.append("None")
                sentvalue.append("None")     
        else:
            if prob_neg - prob_pos > 0.15:
                sentvalue.append(prob_pos)
                sentvalue.append(prob_neg)     
            else:
                sentvalue.append("None")
                sentvalue.append("None")
        senttotal.append(sentvalue) 
                
    return senttotal