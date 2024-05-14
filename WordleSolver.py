import random
from general_funcitons import import_base_wordle_list
from general_funcitons import bot_print, debug_print
from general_funcitons import start_clock, end_clock
from general_funcitons import push_to_txt
from general_funcitons import bot_on, debug, make_files
from info_theory import run_info_theory

MAX_GUESSES = 6 
bot_loops = 10
# This is how many remaining words before we switch guessing algos
# 1000 Seems to be the sweet spot
word_cap = 1000

word_list_path:str = 'WordleList.txt'
perfect_match_path:str = 'After_Perfect_Matches.txt'
black_list_path:str = 'After_Black_Lists.txt'
near_miss_path:str = 'After_Near_Miss.txt'
perfect_match_kick_path:str = 'Kick_After_Perfect_Matches.txt'
black_list_kick_path:str = 'Kick_After_Black_Lists.txt'
near_miss_kick_path:str = 'Kick_After_Near_Miss.txt'

alphabet = [chr(ord('a') + i) for i in range(26)]
word_len = 5
colors = {
        'red': '\033[41m',  # Red background
        'green': '\033[48;5;28m',  # Green background
        'yellow': '\033[43m',  # Yellow background
        'reset': '\033[0m'  # Reset color and attributes
    }
response_options:list[list[int]] = []
for i in range(3):
    for j in range(3):
        for k in range(3):
            for l in range(3):
                for m in range(3):
                    option = [i,j,k,l,m]
                    response_options.append(option)

def pick_wordle_word(word_list:list[str]):
    list_size = len(word_list)
    rand_int = random.randrange(list_size)
    word = word_list[rand_int]
    return word

def calculate_letter_frequency(viable_words:list[str], initial_weight):
    '''
    Letter frequecy is calcualted by counting the occcurance of a letter in a given position
    So the word like apple, would have a frequency dict of the following
    frequency[a] = [1,0,0,0,0]
    frequency[p] = [0,1,1,0,0]
    frequency[l] = [0,0,0,1,0]
    frequency[e] = [0,0,0,0,1]
    These values would get added to a whole list frequency dict to give the frequency of a letter
        in a given index position so we will select the word that has the letters of highest frequency
        in the spaces that they are most frequent.
    The word value is then a composite of the abbreviated lists frequencys after removing for know info,
        and the orginial list to still favor words that are overall morecommon that what our small list 
        may favor. 

    '''
    
    # Gets the value of how often a letter is in a given place
    start = start_clock()
    frequency_dict:dict = {}
    
    # clear out each letter
    for a_letter in alphabet:
        appearances:list[int] = [0,0,0,0,0]
        frequency_dict[a_letter] = appearances
        
    # Grab Each wordle word and incriment by one for every letter in the list
    for word in viable_words:
        for i, letter in enumerate(word):
            frequency_dict[letter][i] += 1

    if initial_weight:
        for letter in alphabet:
            base_value = initial_weight[letter]
            shortened_list_value = frequency_dict[letter]
            new_value = [x + y for x, y in zip(base_value, shortened_list_value)]
            frequency_dict[letter] = new_value
    end_clock('Calculating Letter Frequency', start)
    return frequency_dict

def find_word_value(word:str, frequency_dict:dict):
    word_value:int = 0
    letters = list(word)
    unique_letters = set(letters)
    for letter in unique_letters:
        appearance = word.count(letter)
        letter_index = word.index(letter)
        letter_value = frequency_dict[letter][letter_index]
        for i in range(appearance):
            word_value += int(letter_value/(i+ 1))
    return word_value

def pick_best_word(viable_words:list[str], frequency_dict:dict):
    '''
    To understand how letter frequencys are generated, view the calculate_letter_frequency function.
    A words value is based on the frequency of a letter in its given position based on the remaining 
        viable list, as well as the original list to ensure we still lean towards words that have
        higher frequency letters in general. So for example a list of only cakes and caves, both are 
        k and v and possible options, but because in the original list, k is more commmon, we will try
        cakes first.
    '''
    start = start_clock()
    best_word_value:int = 0
    best_words:list[str] = []
    for word in viable_words:
        word_value = find_word_value(word, frequency_dict)
        if word_value > best_word_value:
            best_words:list[str] = [word]
            best_word_value = word_value
        if word_value == best_word_value:
            best_words.append(word)
    viable_word_count = len(best_words)
    random_int = random.randrange(0,viable_word_count)
    best_word = best_words[random_int]
    end_clock('Picking Best Word', start)
    debug_print(f'Best words {best_words}')
    return best_word

def max_letter_elimination(full_list, word_list, perfect_matches, black_list, frequency_dict):
    '''
    We look at all words in the bulk list, then we pick the word with the best value
    when the perfect letters are given a value of 0
    '''
    for letter in alphabet:
        avg = int(sum(frequency_dict[letter])/5)
        frequency_dict[letter] = [avg,avg,avg,avg,avg]
        present = False
        for word in word_list:
            if letter in word:
                present = True
                continue
        if not present:
            frequency_dict[letter] = [0,0,0,0,0]            
    for entry in black_list:
        try:
            letter = entry[0]
        except IndexError:
            continue
        frequency_dict[letter] = [0,0,0,0,0]
    for entry in perfect_matches:
        try:
            letter = entry[0]
        except IndexError:
            continue
        frequency_dict[letter] = [0,0,0,0,0]
    debug_print(frequency_dict)
    return pick_best_word(full_list, frequency_dict)

def remove_by_blacklist_letters(black_list:list[str], viable_words:list[str]):
    start = start_clock()
    filtered_list:list[str] = []
    kick_list:list[str] = []
    if black_list[0] == '':
        return viable_words
    for word in viable_words:
        kick = False
        for letter in black_list:
            if letter in word:
                kick = True
                word = f'{word} kicked for having a {letter}'
                kick_list.append(word)
                break
        if not kick:
            filtered_list.append(word)
    debug_print(f'Current Words after filtering for black list letters: {len(filtered_list)}')
    end_clock('Removing Blacklisted Letters', start)
    push_to_txt(black_list_kick_path, kick_list)
    return filtered_list

def remove_by_near_miss(near_miss_list:list[list[str, list[int]]], viable_words:list[str]):
    start = start_clock()
    filtered_list:list[str] = []
    kick_list:list[str] = []
    debug_print(f'near miss {near_miss_list}')
    if not near_miss_list:
        debug_print('skipping near misses')
        return viable_words
    for word in viable_words:
        kick = False
        for near_miss in near_miss_list:
            letter = near_miss[0]
            invalid_placement = near_miss[1]
            if letter == '':
                continue
            if not letter in word:
                kick = True
                word = f'{word} kicked for not having {letter}'
                kick_list.append(word)
                break
            for position in invalid_placement:
                if letter == word[position]:
                    kick = True
                    word = f'{word} kicked for having {letter} in position {position + 1}'
                    kick_list.append(word)
                    break
            if kick:
                break
        if kick:
            continue
        filtered_list.append(word)
    debug_print(f'Current Words after filtering for near misses: {len(filtered_list)}')
    #end_clock('Remove Near Misses', start)
    push_to_txt(near_miss_kick_path, kick_list)
    return filtered_list

def remove_by_perfect_match(perfect_match_list:list[list[str, list[int]]], viable_words:list[str]):
    start = start_clock()
    filtered_list:list[str] = []
    kick_list:list[str] = []
    debug_print(f'perfect match {perfect_match_list}')
    if perfect_match_list[0][0] == '':
        return viable_words
    for word in viable_words:
        kick = False
        for match in perfect_match_list:
            letter = match[0]
            valid_placement = match[1]
            for position in valid_placement:
                if not letter == word[position]:
                    kick = True
                    word = f'{word} kicked for not having a {letter} in position {position + 1}'
                    kick_list.append(word)
                    break
            if kick:
                break
        if kick:
            continue   
        filtered_list.append(word)
    #print(f'Current Words after filtering for known placement: {len(filtered_list)}')
    #end_clock('Allow known placement', start)
    push_to_txt(perfect_match_kick_path, kick_list)
    return filtered_list                 

def add_to_black_list(black_list:list, letter:str):
    if black_list[0] == '':
        black_list[0] = letter
        return black_list
    for entry in black_list:
        if letter == entry:
            return black_list
    black_list.append(letter)
    return black_list

def add_to_positional_list(positional_list:list, letter:str, index:int):
    if positional_list[0] == ['', [0]]:
        new_entry = [letter,[index]]
        positional_list[0] = new_entry
        return positional_list
    for i, entry in enumerate(positional_list):
        entry_letter = entry[0]
        entry_indexes = entry[1]
        if letter == entry_letter:
            if index == entry_indexes or index in entry_indexes:
                return positional_list
            entry_indexes.append(index)
            return positional_list
    new_entry = [letter,[index]]
    positional_list[0] = new_entry
    positional_list.append(new_entry)   
    return positional_list

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

def test_guess(test_word:str, test_score:list[int], letter_lists:list, viable_words:list[str]):
    test_black = letter_lists[0].copy()
    test_near_miss = letter_lists[1].copy()
    test_perfect = letter_lists[2].copy()

    for i, value in enumerate(test_score):
        if value == 0:
            test_black = add_to_black_list(test_black, test_word[i])

        if value == 1:
            test_near_miss = add_to_positional_list(test_near_miss, test_word[i], i)

        if value == 2:
            test_perfect = add_to_positional_list(test_perfect, test_word[i], i)
    viable_words = remove_by_blacklist_letters(test_black, viable_words)
    viable_words = remove_by_perfect_match(test_perfect, viable_words)
    viable_words = remove_by_near_miss(test_near_miss, viable_words)
    remaining = len(viable_words)
    return remaining

def evaluate_guess(best_word:str, actual_word:str, letter_lists:list):
    start = start_clock()
    values = [0,0,0,0,0]
    for letter_index in range(word_len):
        if not best_word[letter_index] in actual_word:
            letter_lists[0] = add_to_black_list(letter_lists[0], best_word[letter_index])
        elif not best_word[letter_index] == actual_word[letter_index]:
            values[letter_index] = 1
            # Update the near miss list
            debug_print('adding to near misses')
            letter_lists[1] = add_to_positional_list(letter_lists[1], best_word[letter_index], letter_index)
            
        else:
            # Update the perfect match list
            debug_print('adding to perfect matches')
            values[letter_index] = 2
            letter_lists[2] = add_to_positional_list(letter_lists[2], best_word[letter_index], letter_index)
    end_clock('Evaluating Word', start)
    '''
    print(f'Black List {letter_lists[0]}')
    print(f'near misses {letter_lists[1]}')
    print(f'Perfect matches {letter_lists[2]}')'''
    return letter_lists, values

def display_word_score(word:str, word_score:list[int]):
    start = start_clock()
    for letter_index in range(word_len):
        char = word[letter_index]
        score = word_score[letter_index]
        color_code = colors['reset']
        if score == 1:
            color_code = colors['yellow']
        elif score == 2:
            color_code = colors['green']
        if not bot_on:
            print(f"{color_code}{char}{colors['reset']}", end='')
    bot_print('\n')
    end_clock('Display Score', start)

def init_lists():
    black_list:list[str] = ['']
    match_item:list[str,list[int]] = ['',[0]]
    near_miss_list:list[list[str,list[int]]] = [match_item]
    perfect_match_list:list[list[str,list[int]]] = [match_item]
    return [black_list, near_miss_list, perfect_match_list]

def main():
    bot_print('starting game')
    viable_words = import_base_wordle_list(word_list_path)
    full_wordle_list = import_base_wordle_list(word_list_path)
    letter_lists = init_lists()
    wordle_word:str = ''
    wordle_word = pick_wordle_word(full_wordle_list)
    initial_frequency_dict = calculate_letter_frequency(viable_words, None)
    guesses = 0
    playing = True
    while playing:
        # Gets the freqency of all letters in the list and weights it on inital list frequency
        frequncy_dict = calculate_letter_frequency(viable_words, initial_frequency_dict)
        
        # With the frequency dict, we pick the word that has the highest frequency letters
        
        if 2 < len(viable_words) < word_cap:
            frq_word = max_letter_elimination(full_wordle_list, viable_words, letter_lists[2], letter_lists[0], frequncy_dict)
        else:    
            frq_word = pick_best_word(viable_words, frequncy_dict)
        debug_print(f'The actual word is {wordle_word}')
        print(f'\nThe program suggests the word by frequency: {frq_word}')
        info_word = None
        if len(viable_words) < 5000:
            info_word = run_info_theory(viable_words, full_wordle_list)
            print(f'\nThe program suggests the word by info theory: {info_word}')
        # Ask the user for their guess, evaluate and score it
        if info_word:
            best_word = info_word
        else: 
            best_word = frq_word
        if bot_on:
            if guesses == 0:
                best_word = 'tares'
            guessed_word = best_word
        else:
            guessed_word = get_guess(full_wordle_list)

        letter_lists, word_score = evaluate_guess(guessed_word, wordle_word, letter_lists)
        display_word_score(guessed_word, word_score)

        viable_words = remove_by_blacklist_letters(letter_lists[0], viable_words)
        push_to_txt(black_list_path, viable_words)

        viable_words = remove_by_perfect_match(letter_lists[2], viable_words)
        push_to_txt(perfect_match_path, viable_words)

        viable_words = remove_by_near_miss(letter_lists[1], viable_words)
        push_to_txt(near_miss_path, viable_words)

        guesses += 1
        if guesses > MAX_GUESSES:
            playing = False

        if guessed_word == wordle_word:
            playing = False
    win = False
    if guesses > MAX_GUESSES:
        bot_print('You Lost')
        return guesses, win, wordle_word
    if wordle_word == guessed_word:
        bot_print(f'You won in {guesses} guesses')
        win = True
    return guesses, win, wordle_word

def show_stats(ratio:list[int,bool], loops: int, missed_words:list[str]):
    guesses:int = 0
    wins:int = 0
    for game in ratio:
        win = game[1]
        if not win:
            continue
        guesses += game[0]
        wins += 1
    guess_avg = round(guesses/(loops), 3)
    win_rate = round((wins/(loops))*100, 3)
    print(f'After playing {loops} games. The bot had a winrate of {win_rate}%, with a total average guesses on winning games of {guess_avg}')
    #print(f'The missed words were:{missed_words}.')

if __name__ == '__main__':
    print('starting program')
    loops = bot_loops
    loop = 0
    ratio:list[int,bool] = []
    start = start_clock()
    # Loops For testing speed and acuracy
    missed_words = []
    while loop < loops:
        guesses, win, word = main()
        outcome = [guesses, win]
        ratio.append(outcome)
        loop += 1
        if not win:
            missed_words.append(word)
        if not bot_on:
            break
        print(f'Completed game {loop + 1}')
    if bot_on:
        show_stats(ratio, loops, missed_words)
    end_clock('Total Runtime', start)