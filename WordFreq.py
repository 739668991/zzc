from wordfreqCMD import remove_punctuation, freq, sort_in_descending_order

class WordFreq:
    def __init__(self, s):
        self.s = remove_punctuation(s)

    def get_freq(self):
        return sort_in_descending_order(freq(self.s))
    

if __name__ == '__main__':
    f = WordFreq('BANANA; Banana, apple ORANGE Banana banana.')
    print(f.get_freq())

