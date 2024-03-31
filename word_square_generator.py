import wordmatrix
import wavefunction

size = [4,5]

def get_dictionary_word_list(filename):
    with open(filename, encoding="utf_8") as f:
        # Return the split results, which is all the words in the file.
        return f.read().split()

# Loading words to a dictionary for generation
#dict = get_dictionary_word_list("dictionary_EN.txt")
dict = get_dictionary_word_list("google-10000-english.txt")

table = wordmatrix.Wordmatrix(size, dict)
wfc = wavefunction.Wavefunction(table)

wfc.run()