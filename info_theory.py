import math
import multiprocessing
from WordleSolver import import_base_wordle_list, init_lists
from WordleSolver import start_clock, end_clock, bot_print
from WordleSolver import remove_by_blacklist_letters, remove_by_near_miss, remove_by_perfect_match
from WordleSolver import push_to_txt

word_list_path:str = 'WordleList.txt'

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

def letter_list(word:str, response:list[int]):
    lists = init_lists()
    black_list, near_miss_list, white_list = lists[0], lists[1], lists[2]
    for i, letter_score in enumerate(response):
        entry = [word[i], [i]]
        if letter_score == 0:
            list = black_list
            entry = word[i]
        elif letter_score == 1:
            list = near_miss_list
        else: 
            list = white_list
        if list[0] == '':
            list[0] = entry
            continue
        elif list[0][0] == '':
            list[0] = entry
        else:
            list.append(entry)
    return black_list, white_list, near_miss_list

def find_option_bit_value(response:list[int], word:str, list_size:int, word_list:list[str]):
    word_list_copy = list(word_list)
    black_list, white_list, near_miss_list = letter_list(word, response)
    word_list_copy = remove_by_blacklist_letters(black_list, word_list_copy)
    word_list_copy = remove_by_near_miss(near_miss_list, word_list_copy)
    word_list_copy = remove_by_perfect_match(white_list, word_list_copy)
    end_size = len(word_list_copy)
    if end_size == 0:
        return 0
    p = end_size / list_size
    bits = math.log2(1/p) * p
    return bits

def find_list_bit_value(set, viable_words:list[str]):
    list_size = len(viable_words)
    words_w_bits = []
    for i, word in enumerate(set):
        bit_sum = 0
        for response in response_options:
            bits = find_option_bit_value(response, word, list_size, viable_words)
            bit_sum += bits
        entry = [word, bit_sum]
        words_w_bits.append(entry)
        if i % 10 == 0 and i > 0: 
            print(f'Word #{i}')
    return words_w_bits

def process_set(set:list[str], viable_words:list[str]):
    list_bits = find_list_bit_value(set, viable_words)
    return list_bits

def split_sets(viable_words:list[str]):
    splits = 12
    set_size = len(viable_words) // splits
    sets = []
    for i in range(0,splits):
        start = i * set_size
        end = start + set_size
        if end > len(viable_words):
            end  = len(viable_words)
        set = viable_words[start:end]
        sets.append(set)
    return sets

def main():
    viable_words = import_base_wordle_list(word_list_path)
    sets = split_sets(viable_words)
    find_list_bit_value(viable_words, viable_words)
    '''
    start = start_clock()
    with multiprocessing.Pool() as pool:
        processed_sets = pool.starmap(process_set, [(data_set, viable_words) for data_set in sets])
    end_clock("total process time", start)
    push_to_txt('list_with_bits', processed_sets)
    '''
    
if __name__ == '__main__':
    main()