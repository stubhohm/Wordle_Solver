import math
import random
from general_funcitons import import_base_wordle_list
from general_funcitons import start_clock, end_clock, bot_print, debug_print
from general_funcitons import push_to_txt, push_to_json, pull_from_json
from general_funcitons import score_to_string

word_answer_path:str = 'WordleAnswerList.txt'
word_guess_path:str = 'WordleGuessList.txt'
json_scores:str = 'bits_scores.json'
json_best:str = 'best_words.json'
json_second_list:str = 'second_pick_lists.json'
update_json = False
last_word = 'zymic'
stop_word = last_word

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

def find_list_bit_value(viable_words:list[str], list_dict:dict, answer_size:int):
    bits_dict = {}
    for word in viable_words:
        word_dict = list_dict[word]
        total_bits = 0
        for key in word_dict.keys():
            if key == '22222':
                bits_dict[word] = 10
                return bits_dict
            count = word_dict[key]
            p = count / answer_size
            bits = -math.log2(p) * p
            total_bits += bits
        bits_dict[word] = total_bits
        if word == stop_word:
            break
    debug_print('end')
    return bits_dict

def get_score(score:str, dict:dict):
    try:
        value = dict[score]
    except KeyError:
        value = 1
        return value
    value += 1
    return value

def get_list(score:str, word:str, dict:dict):
    try:
        value = dict[score]
    except KeyError:
        value = [word]
        debug_print(value)
        return value
    value.append(word)
    debug_print(value)
    return value

def find_list_scores(viable_words:list[str], full_list:list[str], list = False):
    ''' 
    This gives the number of words that have any given score
    This is faster than filtering the list down and is simply
    We basically hash the list with the current word and bucket
    based on the guess as a hashing algo key and the target as the 
    hashing algo input.
    '''
    starting_letter = None
    start = start_clock()
    giant_dict = {}
    for guess_word in full_list:
        if starting_letter != guess_word[0]:
            debug_print(guess_word)
            starting_letter = guess_word[0]
        dict = {}
        for target_word in viable_words:
            score = score_guess(guess_word, target_word)
            if list:
                value = get_list(score, target_word, dict)
                dict[score] = value
            else:
                value = get_score(score, dict)
                dict[score] = value
        giant_dict[guess_word] = dict
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

def get_best_list(bit_dict:dict):
    sorted_words = sorted(bit_dict.items(), key=lambda x: x[1], reverse=True)
    largest_keys = [word[0] for word in sorted_words]
    best_list = {}
    for key in largest_keys[:20]:
        best_list[key] = bit_dict[key]
    return best_list

def pick_best_word(bit_dict:dict):
    max_v = -1
    best_word = ''
    for word in bit_dict.keys():
        value = bit_dict[word]
        if value > max_v:
            max_v = value
            best_word = word
    return best_word

def try_look_up(score):
    score_str = score_to_string(score)
    second_words = pull_from_json('second_pick_word_table.json')
    word = second_words['tarse'][score_str]
    debug_print(word)
    return word

def run_info_theory(viable_words:list[str], full_list:list[str], guess_count:int, score:list[int]):
    bits_dict = get_bits_dict(viable_words, full_list, guess_count)
    if guess_count == 1:
        word = try_look_up(score)
    else:
        word = pick_best_word(bits_dict)
    return word

def get_bits_dict(answers:list[str], guesses:list[str], guess_count:int):
    json_dict = pull_from_json(json_scores)
    if not json_dict or update_json or guess_count > 1:
        list_scores = find_list_scores(answers, guesses)
        bits_dict = find_list_bit_value(guesses, list_scores, len(answers))
        push_to_json('test.json', list_scores)
        list_scores = None
    else:
        bits_dict = json_dict
    return bits_dict

def main():
    guess_words = import_base_wordle_list(word_guess_path)
    answer_words = import_base_wordle_list(word_answer_path)
    bits_dict = get_bits_dict(answer_words, guess_words, 0)
    word = pick_best_word(bits_dict)
    best_list = get_best_list(bits_dict)
    print(word)
    if not update_json:
        push_to_json(json_scores, bits_dict)
    push_to_json(json_best, best_list)

def make_second_pick_dictionary():
    best_dict = pull_from_json(json_best)
    guess_words = []
    for key in best_dict.keys():
        guess_words.append(key)
    answer_words = import_base_wordle_list(word_answer_path)
    second = find_list_scores(answer_words, guess_words, True)
    debug_print('testing')
    push_to_json(json_second_list, second)

def evaluate_second_pick_best_words():
    guess_words = import_base_wordle_list(word_guess_path)
    second_best_lists = pull_from_json(json_second_list)
    for word in second_best_lists.keys():
        word_list = second_best_lists[word]
        for response in word_list.keys():
            list = word_list[response]
            print(len(list))
            word = run_info_theory(list, guess_words, 1)
            word_list[response] = word
        push_to_json('second_pick_word_table.json', second_best_lists)

if __name__ == '__main__':
    #main()
    #make_second_pick_dictionary()
    evaluate_second_pick_best_words()