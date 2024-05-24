import time
import json

bot_on = False
debug = False
make_files = True
word_len = 5

def bot_print(print_input):
    if bot_on:
        return
    print(print_input)

def debug_print(print_input):
    if not debug:
        return
    print(print_input)

def start_clock():
    return time.time()

def end_clock(clock_name:str, start_time:float):
    end_time = time.time()
    elapsed_time = end_time - start_time
    debug_print(f"\nElapsed time for {clock_name} Function: {elapsed_time} seconds")

def get_guess(valid_input:list[str]):
    prompt = f'Guess a {word_len} letter word: '
    word = input(prompt)
    word.strip()
    bot_print(word)
    while not word in valid_input:
        bot_print('You must put in a valid five letter word.\nPlease try again')
        word = input(prompt)
        word.strip()
        bot_print(word)
    return word

def score_to_string(score:list[int]):
    if type(score) == str:
        return score
    score_str = ''
    for value in score:
        if value == 0:
            score_str += '0'
        elif value == 1:
            score_str += '1'
        else: 
            score_str += '2'
    return score_str

def push_to_txt(path:str, words:list[str]):
    # If you change toggle to true, you will make updated doc lists of viable words.
    # If you change toggle to false, you will disable this feature.
    if bot_on:
        return
    if not make_files:
        return
    string = '\n'.join(words)
    with open(path, 'w') as file:
        file.write(string)

def push_to_json(path:str, dict:dict):
    if bot_on:
        return
    if not make_files:
        return
    with open(path, 'w') as convert_file: 
        convert_file.write(json.dumps(dict))

def pull_from_json(path):
    try:
        with open(path, 'r') as json_file:
            loaded_dict = json.load(json_file)      
    except FileNotFoundError:
        loaded_dict = None
    return loaded_dict    
    
def import_base_wordle_list(path:str):
    start = start_clock()
    with open(path, 'r') as wordle_text:
        wordle_str = wordle_text.read()
        wordle_array = wordle_str.split()
    end_clock('Importing Wordle List', start)
    return wordle_array

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