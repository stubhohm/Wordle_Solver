from WordleSolver import import_base_wordle_list
from WordleSolver import start_clock, end_clock, bot_print
from WordleSolver import remove_by_blacklist_letters, remove_by_near_miss, remove_by_perfect_match

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

def find_words_bit_value(viable_words:list[str]):
    for word in viable_words:
        for option in response_options:



def main():
    viable_words = import_base_wordle_list(word_list_path)


if __name__ == '__main__':
    main()