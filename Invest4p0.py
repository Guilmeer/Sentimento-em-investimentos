from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.popup import Popup

import Tweets_Treatment as TT
import Twitter_API_Auth as Auth
import itertools
import feedparser
import nltk 
nltk.download('punkt')
nltk.download('stopwords')

e1 = Auth.Twitterapi()

class Invest(App):
    def build(self):
        return Gerenciador()

class Gerenciador(ScreenManager):
    pass

class Menu(Screen):
    pass

class Tweets(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sentDict = None
        self.tweets = None

    def on_pre_enter(self, *args):
        Window.bind(on_keyboard=self.voltar)
    
    def voltar(self, window, key, *args):
        if key == 27:
            App.get_running_app().root.current = 'menu'
            return True

    def on_pre_leave(self, *args):
        Window.unbind(on_keyboard=self.voltar)     

    def Pesquisa(self):
        self.ids.box.clear_widgets()
        pesquisa = self.ids.pesquisa.text
        quantidade = int(self.ids.quantidade.text)
        api = e1.get_api()
        self.tweets = TT.Get_tweets(api, pesquisa, quantidade)  
        for text in self.tweets:
            self.ids.box.add_widget(Tweet(text = 'Usuário: ' + text[0] + '\n' + text[1]))
        self.ids.pesquisa.text = ''
        self.ids.quantidade.text = ''
        if self.tweets != None:
            self.AnalizarSent()

    def AnalizarSent(self):
        tweetText = []
        for text in self.tweets:
            tweetText.append(text[1])
        tokenized = TT.Tokenizer(tweetText)
        df = TT.xlsx()
        self.sentlist = TT.sentBayes(df, tokenized)

    def open_popup(self):
        box = PopupSent()
        try:
            box.changeSent(self.sentlist)
        except: None
        self.popup = Popup(title="Análise de sentimentos", content = box)
        self.popup.open()

class PopupSent(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def changeSent(self, text):
        cleanText = []
        if text != None:
            interList = []
            for each in text:
                interList.append([each[1], each[2]])
            pos = 0
            neg = 0
            for each in [i[0] for i in interList]:
                try:
                    if each != 0.5:
                        pos += each
                except: continue
            for each in [i[1] for i in interList]:
                try:
                    if each != 0.5:
                        neg += each
                except: continue
            if pos > neg:
                senttotal = "Soma do sentimento total foi positivo: " + str(round(pos, 2)) + "\nSoma dos negativos:" + str(round(neg, 2))
            else:
                senttotal = "Soma do sentimento total foi negativo: " + str(round(neg, 2)) + "\nSoma dos positivos:" + str(round(pos, 2))
            senttotal = str(senttotal) + '\n'
            print(senttotal)
            for each in text:
                cleanText.append('pos: ' + str(each[1]) + " neg: " + str(each[2]) + '\n')
            joinText = senttotal + ''.join(cleanText)
            if cleanText != None:
                self.ids.sentimentLevel.text = joinText 
        else:
            self.ids.sentimentLevel.text = "Sem Informação"

class Tweet (BoxLayout):
    def __init__(self, text = '', **kwargs):
        super().__init__(**kwargs)
        self.ids.label.text = text

class Noticias (Screen):
    def __init__(self, text = '', **kwargs):
        super().__init__(**kwargs)

    def on_pre_enter(self, *args):
        Window.bind(on_keyboard=self.voltar)
        
    def voltar(self, window, key, *args):
        if key == 27:
            App.get_running_app().root.current = 'menu'
            return True

    def on_pre_leave(self, *args):
        Window.unbind(on_keyboard=self.voltar)
    
    def Preparar (self, text):
        try:
            self.ids.boxnot.clear_widgets()
        except: pass
        self.MontaNoticia(text)
        
    
    def MontaNoticia(self, text):
        newsfeed = feedparser.parse(text)
        for index, entrie in enumerate(newsfeed.entries):
            self.ids.boxnot.add_widget(Noticia(text= entrie.title + "\n" + entrie.published ))


class Noticia (BoxLayout):
    def __init__(self, text = '', **kwargs):
        super().__init__(**kwargs)
        self.ids.label.text = text

class PopupContent (BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def salvarRSS(self):
        rsstext = self.ids.rss.text
        with open("sample.txt", "a") as file_object:
            file_object.write('\n' + rsstext)

class ListaRSS(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #self.Reload()
    def on_pre_enter(self, *args):
        Window.bind(on_keyboard=self.voltar)
        self.Reload()

    def Reload(self):
        try: self.ids.box.clear_widgets()
        except: pass
        while True:
            try:
                with open("sample.txt", 'r+') as fileObj:
                    for cnt, line in enumerate(fileObj):
                        self.ids.box.add_widget(RSSLink(cnt = str(cnt + 1),text = line))
                break
            except:
                open("sample.txt", 'w')
    
    def voltar(self, window, key, *args):
        if key == 27:
            App.get_running_app().root.current = 'menu'
            return True
    
    def on_pre_leave(self, *args):
        Window.unbind(on_keyboard=self.voltar)
                
    def OpenPopup(self):
        box = PopupContent()
        self.pop = Popup(title='Adicionar RSS', content = box, size_hint=(None,None),
                    size=(300,180))
        self.pop.open()
    
    def ClosePop(self):
        self.pop.dismiss()
    
    def MostrarNoticias(self):
        noticias = ['aa','bb']
        for noticia in noticias:
            self.ids.box.add_widget(Noticia(text = noticia))


class RSSLink(BoxLayout):
    def __init__(self, cnt, text, **kwargs):
        super().__init__(**kwargs)
        self.ids.count.text = cnt
        self.ids.label.text = text
     

Invest().run()
