import math
from general_funcitons import start_clock, end_clock
from general_funcitons import debug_print
from general_funcitons import push_to_json

red = 'red'
orange = 'orange'
blue = 'blue'
pink = 'pink'
green = 'green'
yellow = 'yellow'

black = 'black'
white = 'white'
empty = 'empty'

code_pegs = [red, orange, blue, pink, green, yellow]
response_pegs = [black, white, empty]

solutions = []
for peg_1 in code_pegs:
    for peg_2 in code_pegs:
        for peg_3 in code_pegs:
            for peg_4 in code_pegs:
                answer = [peg_1, peg_2, peg_3, peg_4]
                solutions.append(answer)
solution_count = len(solutions)
guesses = list(solutions)
debug_print(solution_count)

def best_guess(bit_dict:dict):
    max_v = -1
    best_guess = ''
    best_guesss = []
    for guess in bit_dict.keys():
        value = bit_dict[guess]
        if value > max_v:
            max_v = value
            best_guess = guess
            best_guesss = []
        if value == max_v:
            best_guesss.append(guess)  

    best_guess = best_guesss[0]
    print(best_guesss)
    print(best_guess)
    return best_guess, best_guesss

def find_list_bit_value(guesses:list[str], list_dict:dict, answer_size:int):
    bits_dict = {}
    for guess in guesses:
        guess_str = '.'.join(guess)
        guess_dict = list_dict[guess_str]
        total_bits = 0
        for key in guess_dict.keys():
            if key == '22222':
                bits_dict[guess_str] = 10
                return bits_dict
            count = guess_dict[key]
            p = count / answer_size
            bits = -math.log2(p) * p
            total_bits += bits
        bits_dict[guess_str] = total_bits
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

def get_list(score:str, guess:str, dict:dict):
    try:
        value = dict[score]
    except KeyError:
        value = [guess]
        return value
    value.append(guess)
    return value

def score_code(guess:list[str], solution:list[str]):
    score = []
    assessed = ['','','','']
    for i, peg_s in enumerate(solution):
        for j, peg_g in enumerate(guess):
            if peg_g == peg_s and assessed[j] == 0:
                assessed[j] = 1
                if i == j:
                    score.append(black)
                    break
                else:
                    score.append(white)
                    break
    score_str = '.'.join(score)
    return score_str

def find_list_scores(solutions:list[str], guesses:list[str], list = False):
    ''' 
    This gives the number of guesss that have any given score
    This is faster than filtering the list down and is simply
    We basically hash the list with the current guess and bucket
    based on the guess as a hashing algo key and the target as the 
    hashing algo input.
    '''
    starting_letter = None
    start = start_clock()
    giant_dict = {}
    for guess in guesses:
        if starting_letter != guess[0]:
            debug_print(guess)
            starting_letter = guess[0]
        dict = {}
        for solution in solutions:
            score = score_code(guess, solution)
            if list:
                value = get_list(score, guess, dict)
                dict[score] = value
            else:
                value = get_score(score, dict)
                dict[score] = value
        str_guess= '.'.join(guess)
        giant_dict[str_guess] = dict
    push_to_json('two_guess_MM.json', giant_dict)
    end_clock('hashing guesss', start)
    return giant_dict

def find_second_guess(giant_dict, guesses):
    guess_dict = {}
    for entry in giant_dict.keys():
        results = giant_dict[entry]
        guess_dict = find_list_scores(results, guesses)
        guess_bits = find_list_bit_value(guesses, guess_dict, len(guess_dict))
        best, best_list = best_guess(guess_bits)

giant_dict = find_list_scores(solutions, guesses)
giant_dict = find_list_scores(solutions, guesses, True)
#second_bits_dict = find_second_guess(giant_dict, guesses)
#bits_dict = find_list_bit_value(guesses, giant_dict, len(giant_dict))
#best, best_list = best_guess(bits_dict)
#push_to_json('master_mind.json', giant_dict)
#push_to_json('master_mind_list.json', bits_dict)