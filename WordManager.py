import nltk
from nltk.corpus import stopwords
from pythainlp.tokenize import word_tokenize
from pythainlp.tag import pos_tag
from pythainlp.corpus import thai_stopwords
import re
from pythainlp.util import rank
class WordManager:

    def counter(self, content):
        text = nltk.word_tokenize(content)
        freq = nltk.FreqDist(text)
        return freq.most_common(10)

    def counter_th(self, content):
        text = word_tokenize(content)
        freq = rank(text)
        return freq.most_common(10)


    def get_nouns(self, content):
        tokenized = nltk.word_tokenize(content)
        nouns = [word for (word, pos) in nltk.pos_tag(tokenized) if pos == "NNP"] 
        return nouns

    def get_nouns_th(self, content):
        text = word_tokenize(content, engine="attacut")
        noun_type = ['PRON', 'PROPN', 'NOUN', 'NPRP', 'NTTL', 'NCNM']
        nouns = [word for (word, pos) in pos_tag(text, corpus='pud') if word!=" " and pos in noun_type]
        print(pos_tag(text,corpus='pud'))
        return nouns
    
    def clean_text_th(self, text):
        thai_stopword = set(thai_stopwords())
        token = word_tokenize(text, engine='attacut')
        text_list = [t for t in token if t not in thai_stopword]
        text = " ".join(text_list)
        text = self.remove_url_th(text)
        return text

    def clean_text(self, text):
        # text = text.lower()
        eng_stopword = set(stopwords.words('english'))
        token = nltk.word_tokenize(text)
        text_list = [t for t in token if t not in eng_stopword]
        text = " ".join(text_list)
        text = self.remove_url_th(text)
        return text
    
    def remove_url(self, txt):
        """Replace URLs found in a text string with nothing 
        (i.e. it will remove the URL from the string).

        Parameters
        ----------
        txt : string
            A text string that you want to parse and remove urls.

        Returns
        -------
        The same txt string with url's removed.
        """

        return " ".join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", txt).split())


    # In[ ]:


    def remove_url_th(self, txt):
        """Replace URLs found in a text string with nothing 
        (i.e. it will remove the URL from the string).

        Parameters
        ----------
        txt : string
            A text string that you want to parse and remove urls.

        Returns
        -------
        The same txt string with url's removed.
        """

        return " ".join(re.sub("([^\u0E00-\u0E7Fa-zA-Z' ]|^'|'$|''|(\w+:\/\/\S+))", "", txt).split())

if __name__ == '__main__':
    w = WordManager()
    # text = "ทดสอบระบบครับ พสิษฐ์ทำจะแบบนี้ทำไมครับ โรนัลโด้เก่งมาก"
    # text =  "ทดสอบระบบครับ พสิษฐ์ทำจะแบบนี้ทำไมครับ โรนัลโด้เก่งมาก โรนัลโด้สุดยอด"
    # text =  "Hi. My name is John. How are you? John is my best friend."
    # text = w.clean_text(text)
    # # n = w.get_nouns_th(text)
    # print(w.counter(text))

    # text =  "ทดสอบระบบครับ พสิษฐ์ทำจะแบบนี้ทำไมครับ โรนัลโด้เก่งมาก โรนัลโด้สุดยอด"
    # text = w.clean_text_th(text)
    # w.get_nouns_th(text)
    print(stopwords.words('english'))
    print(thai_stopwords())