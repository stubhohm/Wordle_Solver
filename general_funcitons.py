import time
import json

bot_on = False
debug = False
make_files = False

def bot_print(print_input):
    if bot_on:
        return
    print(print_input)

def debug_print(print_input):
    if debug:
        return
    print(print_input)

def start_clock():
    return time.time()

def end_clock(clock_name:str, start_time:float):
    end_time = time.time()
    elapsed_time = end_time - start_time
    debug_print(f"\nElapsed time for {clock_name} Function: {elapsed_time} seconds")

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

def import_base_wordle_list(path:str):
    start = start_clock()
    with open(path, 'r') as wordle_text:
        wordle_str = wordle_text.read()
        wordle_array = wordle_str.split()
    end_clock('Importing Wordle List', start)
    return wordle_array