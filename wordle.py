import requests
import random
import string
import pandas as pd
import logging
import sys


logging.basicConfig(stream=sys.stderr, level=logging.ERROR)
# logging.basicConfig(stream=sys.stderr, level=logging.INFO)

N = 5
GUESSES = 100
URL = r'https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt'
# URL = r'https://www-cs-faculty.stanford.edu/~knuth/sgb-words.txt'
MASTER_WORD_LIST = [word.strip() for word in requests.get(URL).text.split("\n")]
WORD_LIST = [x for x in MASTER_WORD_LIST if len(x) == N]

class Solver:
    def __init__(self, N=5):
        self.N = N
        self.guesses = []
        self.feedback = []
        self.word_list = WORD_LIST
        self.freq = self.get_freq()
        self.next_guesses, self.next_guess = self.get_next_guess()

    def get_freq(self):
        return pd.DataFrame([{let: sum([1 if word[i] == let else 0 for word in self.word_list]) for let in string.ascii_lowercase} for i in range(N)]).transpose()

    def get_score(self, word):
        return sum([self.freq.loc[word[i], i] for i in range(self.N)]) * len(set(word)) / len(word)

    def get_next_guess(self):
        scores = list(map(lambda word: self.get_score(word), self.word_list))
        next_guesses = pd.DataFrame([{"Word": word, "Score": score} for word, score in zip(self.word_list, scores)]).sort_values("Score", ascending=False).reset_index()
        return next_guesses, next_guesses.loc[0, "Word"]
    
    def add_guess(self, word, result):
        self.guesses.append(word)
        self.feedback.append(result)
        right_letters = set([word[i] for i in range(N) if result[i] > 0])
        right_place = set([(i, word[i]) for i in range(N) if result[i] == 2])
        temp = []
        for w in self.word_list:
            # new word must have all the right letters (and none of the wrong ones)
            if (set(w) & set(word)) == right_letters:
                # all letters that were in the correct place must stay there
                if (set(enumerate(w)) & right_place) == right_place:
                    # right letters in the wrong place must be moved
                    if (set(enumerate(w)) & set(enumerate(word))) | right_place == right_place:
                        temp.append(w)
        self.word_list = temp
        self.freq = self.get_freq()
        self.next_guesses, self.next_guess = self.get_next_guess()
        # logging.info(f"next guess is: {self.next_guess}")
                
class Puzzle:
    def __init__(self, word=None):
        self.guesses = []
        if word:
            self.word = word
        else:
            self.word = random.choice(WORD_LIST)

    def guess(self, word):
        logging.info(f"you guessed {word}")
        self.guesses.append(word)
        temp = []
        for i, let in enumerate(word):
            if let == self.word[i]:
                temp.append(2)
            elif let in self.word:
                temp.append(1)
            else:
                temp.append(0)
        logging.info(temp)
        if word == self.word:
            logging.info(f"solved in {len(self.guesses)} tries!")
        elif len(self.guesses) >= GUESSES:
            logging.info(f"failed to solve in {GUESSES} tries. The word was {self.word}.")
            return None
        else:
            logging.info(f"you have {GUESSES-len(self.guesses)} guesses remaining.")
        return temp


# %%
# For playing the wordle!
a = Solver()
a.add_guess("cares",[0,0,1,0,2])
a.add_guess("grots",[0,2,0,1,2])
a.add_guess("trims",[2,2,0,0,2])
# a.add_guess("",[0,2,2,1,0])
# # a.add_guess("",[0,0,0,0,0])

# Some generic data analysis.
# a = Solver().freq
# b = a.sum(axis=1)
# c = b.sort_values(ascending=False)
# a0 = a.sort_values(0, ascending=False).iloc[:5,0]
# a1 = a.sort_values(1, ascending=False).iloc[:5,1]
# a2 = a.sort_values(2, ascending=False).iloc[:5,2]
# a3 = a.sort_values(3, ascending=False).iloc[:5,3]
# a4 = a.sort_values(4, ascending=False).iloc[:5,4]

# Solve for every word


# with open(r'word_list.txt', 'r') as f:
#     WORD_LIST = [x.strip('" \n') for x in f.read().split(",")]

# a = Solver(N=N)
# b = Puzzle(word)
# for i in range(GUESSES):
#     result = b.guess(a.next_guess)
#     if a.next_guess == b.word or result == None:
#         count.append(len(b.guesses))
#         break
#     a.add_guess(a.next_guess, result)



