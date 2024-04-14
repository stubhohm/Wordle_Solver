import time
import random
path = 'WordList.txt'
alphabet = [chr(ord('a') + i) for i in range(26)]
word_len = 5
colors = {
        'red': '\033[41m',  # Red background
        'green': '\033[42m',  # Green background
        'yellow': '\033[43m',  # Yellow background
        'reset': '\033[0m'  # Reset color and attributes
    }

def start_clock():
    return time.time()

def end_clock(clock_name:str, start_time:float):
    elapsed_time = time.time() - start_time
    print(f"Elapsed time for {clock_name} Function: {elapsed_time} seconds")

def import_base_wordle_list(path:str):
    start = start_clock()
    with open(path, 'r') as wordle_text:
        wordle_str = wordle_text.read()
        wordle_array = wordle_str.split('')
    end_clock('Importing Wordle List', start)
    return wordle_array

def pick_wordle_word(word_list:list[str]):
    list_size = len(word_list)
    rand_int = random.randrange(list_size)
    word = word_list[rand_int]
    return word

def calculate_letter_frequency(viable_words:list[str]):
    start = start_clock()
    frequency_dict:dict
    for letter in alphabet:
        appearances = 0
        for word in viable_words:
            appearances += word.count(letter)
        frequency_dict[letter] = appearances
    end_clock('Calculating Letter Frequency', start)
    return frequency_dict

def find_word_value(word:str, frequency_dict:dict):
    word_value:int
    letters = list(word)
    unique_letters = set(letters)
    for letter in unique_letters:
        appearance = word.count(letter)
        letter_value = frequency_dict[letter]
        for i in len(range(appearance)):
            word_value += int(letter_value/i)
    return word_value

def pick_best_word(viable_words:list[str], frequency_dict:dict):
    start = start_clock()
    best_word_value:int
    best_words:list[str]
    for word in viable_words:
        word_value = find_word_value(word, frequency_dict)
        if word_value > best_word_value:
            best_words:list[str] = [word]
            print(best_words)
        if word_value == best_word_value:
            best_words.append(word)
            print(best_words)
    viable_word_count = len(best_words)
    random_int = random.randrange(0,viable_word_count)
    best_word = best_words[random_int]
    end_clock('Picking Best Word', start)
    return best_word

def remove_by_blacklist_letters(black_list:list[str], viable_words:list[str]):
    start = start_clock()
    filtered_list = []
    for letter in black_list:
        for word in viable_words:
            if letter in word:
                continue
            filtered_list.appen(word)
    print(f'Current Words after filtering for black list letters: {len(filtered_list)}')
    end_clock('Removing Blacklisted Letters', start)
    return filtered_list

def remove_by_near_miss(near_miss_list:list[list[str, list[int]]], viable_words:list[str]):
    start = start_clock()
    filtered_list:list[str] = []
    for word in viable_words:
        kick = False
        for near_miss in near_miss_list:
            letter = near_miss[0]
            invalid_placement = near_miss[1]
            for position in invalid_placement:
                if letter == word[position]:
                    kick = True
                    break
            if kick:
                break
        if kick:
            continue
        filtered_list.append(word)
    print(f'Current Words after filtering for near misses: {len(filtered_list)}')
    end_clock('Remove Near Misses', start)
    return filtered_list

def filter_by_perfect_match(perfect_match_list:list[list[str, list[int]]], viable_words:list[str]):
    start = start_clock()
    filtered_list:list[str] = []
    for word in viable_words:
        kick = False
        for match in perfect_match_list:
            letter = match[0]
            valid_placement = match[1]
            for position in valid_placement:
                if not letter == word[position]:
                    kick = True
                    break
            if kick:
                break
        if kick:
            continue
        filtered_list.append(word)
    print(f'Current Words after filtering for known placement: {len(filtered_list)}')
    end_clock('Allow known placement', start)
    return filtered_list                 

def add_to_black_list(black_list:list, letter:str):
    for entry in black_list:
        if letter == entry:
            return
    black_list.append(letter)
    return black_list

def add_to_positional_list(positional_list:list, letter:str, index:int):
    for i, entry in enumerate(positional_list):
        entry_letter = entry[0]
        entry_indexes = entry[1]
        if letter == entry_letter:
            if index in entry_indexes:
                continue
            updated_indexes = entry_indexes.append(index)
            updated_entry = [entry_letter, updated_indexes]
            positional_list[i] = updated_entry
            return positional_list
    new_entry = [letter,[index]]
    positional_list.append(new_entry)
    return positional_list

def get_guess(valid_input:list[str]):
    prompt = f'Guess a {word_len} letter word: '
    word = input(prompt)
    word.strip()
    print(word)
    while not word in valid_input:
        print('You must put in a valid five letter word.\nPlease try again')
        word = input(prompt)
        word.strip()
        print(word)
    return word

def evaluate_guess(best_word:str, actual_word:str, letter_list:list):
    start = start_clock
    values = [0,0,0,0,0]
    for letter_index in range(word_len):
        if not best_word[letter_index] in actual_word:
            letter_list[0] = add_to_black_list(letter_list[0], best_word[letter_index])
            continue
        if not best_word[letter_index] == actual_word[letter_index]:
            values[letter_index] = 1
            # Update the near miss list
            letter_list[1] = add_to_positional_list(letter_list[2], best_word[letter_index], letter_index)
        else:
            # Update the perfect match list
            values[letter_index] = 2
            letter_list[2] = add_to_positional_list(letter_list[1], best_word[letter_index], letter_index)     
    end_clock('Evaluating Word', start)
    return letter_list, values

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
        print(f"{color_code}{char}{colors['reset']}", end='')
    end_clock('Display Score', start)


def main():
    viable_words = import_base_wordle_list(path)
    full_wordle_list = import_base_wordle_list(path)
    black_list:list[str]
    near_miss_list:list[str,list[int]]
    perfect_match_list:list[str,list[int]]
    letter_lists = [black_list, near_miss_list, perfect_match_list]
    wordle_word:str
    wordle_word = pick_wordle_word(full_wordle_list)
    while len(viable_words) > 1:
        frequncy_dict = calculate_letter_frequency(viable_words)
        best_word = pick_best_word(viable_words, frequncy_dict)
        print(f'The program suggests the word: {best_word}')
        print(f'The actual word is {wordle_word}')
        guessed_word = get_guess(full_wordle_list)
        letter_lists, word_score = evaluate_guess(guessed_word, wordle_word, letter_lists)
        display_word_score(guessed_word, word_score)
        viable_words = filter_by_perfect_match(letter_lists[2], viable_words)
        viable_words = remove_by_blacklist_letters(letter_lists[0], viable_words)
        viable_words = remove_by_near_miss(letter_lists[1], viable_words)

if __name__ == '__main__':
    print('starting program')
    main()
        