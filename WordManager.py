import nltk
from nltk.corpus import stopwords
import re
class WordManager:

    def get_nouns(self, content):
        tokenized = nltk.word_tokenize(content)
        nouns = [word for (word, pos) in nltk.pos_tag(tokenized) if pos == "NNP"] 
        return nouns
    
    def clear_text(self, text):
        text = text.lower()
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
