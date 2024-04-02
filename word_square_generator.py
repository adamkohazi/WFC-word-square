import wordmatrix
import wavefunction

size = [5,5]

def optimize_dictionary (lengths, dict):
    opt_dict = []
    for word in dict:
        if len(word) in lengths:
            if word.isalpha():
                opt_dict.append(word.lower())
    return opt_dict

def get_dictionary_word_list(filename):
    with open(filename, encoding="utf_8") as f:
        # Return the split results, which is all the words in the file.
        return f.read().split()

# Loading words to a dictionary for generation
dict = get_dictionary_word_list("dictionary_EN.txt")
#dict = get_dictionary_word_list("google-10000-english.txt")
dict = optimize_dictionary(size, dict)

table = wordmatrix.Wordmatrix(size, dict)
wfc = wavefunction.Wavefunction(table)

wfc.run()