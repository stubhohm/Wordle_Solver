import math
import random
from general_funcitons import import_base_wordle_list
from general_funcitons import start_clock, end_clock, bot_print
from general_funcitons import push_to_txt, push_to_json
from general_funcitons import bot_on, debug, make_files

word_list_path:str = 'WordleList.txt'
stop_word = 'zymic'

# define response options
response_options:list[list[int]] = []
for i in range(3):
    for j in range(3):
        for k in range(3):
            for l in range(3):
                for m in range(3):
                    option = [i,j,k,l,m]
                    response_options.append(option)
total_responses = len(response_options)

def find_list_bit_value(viable_words:list[str], list_dict:dict ):
    list_size = len(viable_words)
    bits_dict = {}
    for word in viable_words:
        word_bits = {}
        word_dict = list_dict[word]
        total_bits = 0
        for key in word_dict.keys():
            count = word_dict[key]
            p = count / list_size
            bits = -math.log2(p) * p
            total_bits += bits
        bits_dict[word] = total_bits
        if word == stop_word:
            print('broke')
            break
    return bits_dict
   
def find_list_scores(viable_words:list[str], full_list:list[str]):
    ''' 
    This gives the number of words that have any given score
    This is faster than filtering the list down and is simply
    We basically hash the list with the current word and bucket
    based on the guess as a hashing algo key and the target as the 
    hashing algo input.
    '''
    start = start_clock()
    giant_dict = {}
    for guess_word in full_list:
        dict = {}
        for target_word in viable_words:
            score = score_guess(guess_word, target_word)
            try:
                value = dict[score]
            except KeyError:
                dict[score] = 1
                continue
            value += 1
            dict[score] = value
        giant_dict[guess_word] = dict
        if guess_word == stop_word:
            print('broke')
            break
    end_clock('hashing words', start)
    return giant_dict

def score_guess(guess:str, target:str):
    word_score = ['0', '0', '0', '0', '0']
    guess_copy = list(guess)
    target_copy = list(target)
    for i, g_letter in enumerate(guess_copy):
        for j, t_letter in enumerate(target_copy):
            if g_letter == t_letter:
                if i == j:
                    word_score[i] = '2'
                else:
                    word_score[i] = '1'
                target_copy[j] = '*'
                guess_copy[i] = '*'
                break
        word_str = ''.join(word_score)
    return word_str

def pick_best_word(bit_dict:dict):
    max_v = 0
    best_word = ''
    for word in bit_dict.keys():
        value = bit_dict[word]
        if value > max_v:
            max_v = value
            best_word = word
    return best_word

def run_info_theory(viable_words, full_list):
    list_scores = find_list_scores(viable_words, full_list)
    bits_dict = find_list_bit_value(viable_words, list_scores)
    list_scores = None
    word = pick_best_word(bits_dict)
    return word

def main():
    viable_words = import_base_wordle_list(word_list_path)
    list_scores = find_list_scores(viable_words, viable_words)
    bits_dict = find_list_bit_value(viable_words, list_scores)
    list_scores = None
    word = pick_best_word(bits_dict)
    print(word)
    push_to_json('bits_scores', bits_dict)
if __name__ == '__main__':
    main()