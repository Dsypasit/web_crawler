import nltk
class WordManager:

    def get_nouns(self, content):
        tokenized = nltk.word_tokenize(content)
        nouns = [word for (word, pos) in nltk.pos_tag(tokenized) if pos == "NNP"] 
        return nouns