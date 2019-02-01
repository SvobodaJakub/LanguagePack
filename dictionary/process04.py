from collections import defaultdict
#import difflib  # TODO? find hunspell words similar to the user dictionary to figure out the proper counterparts to frequent typos; it is very slow

# * inputs: user dictionary, aosp dict with frequencies, hunspell, various
#   communications

# * outputs: aosp-style dict with frequencies and all the words

# * split user dict into one that is proper czech (hunspell) and that is not (not
#   matching hunspell), save the non-matching to a separate file (that should be
#   imported into android as THE user dictionary)

# * substrings of the inputs are matched together to approximately figure out which
#   part of the hunspell dictionary to include

# * you can tweak the code based on the number of words you want in the output dictionary

def remove_diacritics(s):
    return s.replace("ě", "e").replace("š", "s").replace("č", "c").replace("ř", "r").replace("ž", "z").replace("ý", "y").replace("á", "a").replace("í", "i").replace("é", "e").replace("ď", "d").replace("ť", "t").replace("ň", "n").replace("ů", "u").replace("ú", "u").replace("ó", "o")

# unmunch cs_CZ.dic cs_CZ.aff
unmunch = set()
unmunch_nodiacritics = set()
unmunch_nodiacritics_to_diacritics = defaultdict(set)

# from android user dictionary - manually added
userwords = set()
userwords_nodiacritics_and_lower = set()

# gathered from various communication and files, contains a lot of nonsense
othercommwords = set()
othercommwords_nodiacritics = set()

# unmunch cs_CZ.dic cs_CZ.aff and conversion to UTF-8
for line in open('unmunch01.txt'):
    linestrip = line.strip()
    unmunch.add(linestrip)
    line_no_dia = remove_diacritics(linestrip).lower()
    unmunch_nodiacritics.add(line_no_dia)
    unmunch_nodiacritics_to_diacritics[line_no_dia].add(linestrip)

# from android user dictionary - manually added
for line in open('UserWords.xml'):
    if 'value word="' in line:
        word = line.split('word="')[1].split('"/')[0].strip()
        userwords.add(word)
        userwords_nodiacritics_and_lower.add(word.lower())
        userwords_nodiacritics_and_lower.add(remove_diacritics(word.lower()))
        ##TODO print(str(difflib.get_close_matches(word, unmunch)))

# TODO generate this by taking all my communications and splitting out (onto separate lines) runs of (TODO sth like) [a-zA-ZěščřžýáíéďťňůúóĚŠČŘŽÝÁÍÉĎŤŇŮÚÓ]
# gathered from various communication and files, contains a lot of nonsense
# find othercomm/ -type f -exec cat '{}' ';' | grep -a -v -E '^[^ ]{30,}$' | grep -a -E '[a-zA-ZěščřžýáíéďťňůúóĚŠČŘŽÝÁÍÉĎŤŇŮÚÓ]' | sed -r 's/[^a-zA-ZěščřžýáíéďťňůúóĚŠČŘŽÝÁÍÉĎŤŇŮÚÓ]+/\n/g' | grep -a -E '^.{2,25}$' | sort -u | iconv -f utf-8 -t utf-8 -c > othercomm.txt
for line in open('othercomm.txt'):
    othercommwords.add(line.strip())
    othercommwords.add(line.strip().lower())
    othercommwords_nodiacritics.add(remove_diacritics(line.strip().lower()))

# original dict from anysoftkeyboard with frequencies
# word : freq
anysoftkeyboard_orig = {}
# original order starting at 0 : word
anysoftkeyboard_orig_order = {}
anysoftkeyboard_orig_order_counter = 0
for line in open('cs_wordlist.combined'):
    line_split = line.strip().split(",")
    if not line_split[0].startswith("word="):
        continue
    word = line_split[0].split("=")[1]
    freq = int( line_split[1].split("=")[1] )
    anysoftkeyboard_orig[word] = freq
    anysoftkeyboard_orig_order[anysoftkeyboard_orig_order_counter] = word
    anysoftkeyboard_orig_order_counter += 1

# the resulting to-be-output dict
# word : freq
anysoftkeyboard_new = {}
for word, freq in anysoftkeyboard_orig.items():
    anysoftkeyboard_new[word] = freq

def add_to_output_dict_if_not_there(word, freq):
    if word not in anysoftkeyboard_new:
        if not word:
            # do not insert empty words
            return
        if len(word) < 3:
            # do not insert too short words
            return
        anysoftkeyboard_new[word] = freq

# these are only the non-valid words from user dict
# these should be added back to the android's user dict
# (these don't belong to the keyboard's built-in dictionary)
words_only_in_userwords = userwords.difference(unmunch)
_del = set()
for word in words_only_in_userwords:
    if word.lower() in unmunch:
        _del.add(word)
    if remove_diacritics(word.lower()) in unmunch:
        _del.add(word)
words_only_in_userwords = words_only_in_userwords.difference(_del)

# this is a shitload of valid words that are not in the user dict
# probably useless
words_only_in_unmunch = unmunch.difference(userwords)

# these are the valid words from the user dict
words_in_both_userwords_unmunch = userwords.intersection(unmunch)

# these are the valid words from other communications
words_in_both_othercomm_unmunch = othercommwords.intersection(unmunch)
words_in_both_othercomm_unmunch_no_diacritics = othercommwords_nodiacritics.intersection(unmunch_nodiacritics)
for word_n_d in words_in_both_othercomm_unmunch_no_diacritics:
    for word in unmunch_nodiacritics_to_diacritics[word_n_d]:
        words_in_both_othercomm_unmunch.add(word)

userwords_subwords = set()
for word in userwords:
    userwords_subwords.add(word)
    userwords_subwords.add(word[1:])
    userwords_subwords.add(word[2:])
    userwords_subwords.add(word[3:])
    # userwords_subwords.add(word[4:])
    userwords_subwords.add(word[:-1])
    userwords_subwords.add(word[1:-1])
    userwords_subwords.add(word[2:-1])
    userwords_subwords.add(word[3:-1])
    # userwords_subwords.add(word[4:-1])
    userwords_subwords.add(word[:-2])
    userwords_subwords.add(word[1:-2])
    userwords_subwords.add(word[2:-2])
    userwords_subwords.add(word[3:-2])
    # userwords_subwords.add(word[4:-2])
    # userwords_subwords.add(word[:-3])
    userwords_subwords.add(word[1:-3])
    userwords_subwords.add(word[2:-3])
    userwords_subwords.add(word[3:-3])
    # userwords_subwords.add(word[4:-3])
    # userwords_subwords.add(word[:-4])
    # userwords_subwords.add(word[1:-4])
    # userwords_subwords.add(word[2:-4])
    # userwords_subwords.add(word[3:-4])
    # userwords_subwords.add(word[4:-4])

# words and subwords that are longer than 5
subwords_in_userwords_longer_than_5 = set([x for x in userwords_subwords if len(x) > 5 ])

# because there's a lot of rubbish, only the valid words are used for subword matching
othercomm_subwords = set()
for word in words_in_both_othercomm_unmunch:
    othercomm_subwords.add(word)
    othercomm_subwords.add(word[1:])
    othercomm_subwords.add(word[2:])
    # othercomm_subwords.add(word[3:])
    # othercomm_subwords.add(word[4:])
    othercomm_subwords.add(word[:-1])
    othercomm_subwords.add(word[1:-1])
    othercomm_subwords.add(word[2:-1])
    # othercomm_subwords.add(word[3:-1])
    # othercomm_subwords.add(word[4:-1])
    othercomm_subwords.add(word[:-2])
    othercomm_subwords.add(word[1:-2])
    othercomm_subwords.add(word[2:-2])
    # othercomm_subwords.add(word[3:-2])
    # othercomm_subwords.add(word[4:-2])
    # othercomm_subwords.add(word[:-3])
    # othercomm_subwords.add(word[1:-3])
    # othercomm_subwords.add(word[2:-3])
    # othercomm_subwords.add(word[3:-3])
    # othercomm_subwords.add(word[4:-3])
    # othercomm_subwords.add(word[:-4])
    # othercomm_subwords.add(word[1:-4])
    # othercomm_subwords.add(word[2:-4])
    # othercomm_subwords.add(word[3:-4])
    # othercomm_subwords.add(word[4:-4])

# words and subwords that are longer than 5
subwords_in_othercomm_longer_than_5 = set([x for x in othercomm_subwords if len(x) > 5 ])

# words and subwords from unmunch dict and their mapping to all originals from the dict
# subword : set(original, original, original, ...)
unmunch_subwords = defaultdict(set)
for unmunch_word in unmunch:
    if len(unmunch_word) > 4:
        unmunch_subwords[unmunch_word].add(unmunch_word)
    if len(unmunch_word[1:]) > 4:
        unmunch_subwords[unmunch_word[1:]].add(unmunch_word)
    if len(unmunch_word[2:]) > 4 and len(unmunch_word[2:]) < 7: # TODO disable again?
        unmunch_subwords[unmunch_word[2:]].add(unmunch_word)
    # if len(unmunch_word[3:]) > 4:
    #     unmunch_subwords[unmunch_word[3:]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[4:]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[5:]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[6:]].add(unmunch_word)

    if len(unmunch_word[:-1]) > 4:
        unmunch_subwords[unmunch_word[:-1]].add(unmunch_word)
    if len(unmunch_word[1:-1]) > 4:
        unmunch_subwords[unmunch_word[1:-1]].add(unmunch_word)
    # if len(unmunch_word[2:-1]) > 4:
    #     unmunch_subwords[unmunch_word[2:-1]].add(unmunch_word)
    # if len(unmunch_word[3:-1]) > 4:
    #     unmunch_subwords[unmunch_word[3:-1]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[4:-1]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[5:-1]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[6:-1]].add(unmunch_word)

    if len(unmunch_word[:-2]) > 4 and len(unmunch_word[:-2]) < 7: # TODO disable again?
        unmunch_subwords[unmunch_word[:-2]].add(unmunch_word)
    # if len(unmunch_word[1:-2]) > 4:
    #     unmunch_subwords[unmunch_word[1:-2]].add(unmunch_word)
    # if len(unmunch_word[2:-2]) > 4:
    #     unmunch_subwords[unmunch_word[2:-2]].add(unmunch_word)
    # if len(unmunch_word[3:-2]) > 4:
    #     unmunch_subwords[unmunch_word[3:-2]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[4:-2]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[5:-2]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[6:-2]].add(unmunch_word)

    # if len(unmunch_word[:-3]) > 4:
    #     unmunch_subwords[unmunch_word[:-3]].add(unmunch_word)
    # if len(unmunch_word[1:-3]) > 4:
    #     unmunch_subwords[unmunch_word[1:-3]].add(unmunch_word)
    # if len(unmunch_word[2:-3]) > 4:
    #     unmunch_subwords[unmunch_word[2:-3]].add(unmunch_word)
    # if len(unmunch_word[3:-3]) > 4:
    #     unmunch_subwords[unmunch_word[3:-3]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[4:-3]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[5:-3]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[6:-3]].add(unmunch_word)

    # unmunch_subwords[unmunch_word[:-4]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[1:-4]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[2:-4]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[3:-4]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[4:-4]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[5:-4]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[6:-4]].add(unmunch_word)

    # unmunch_subwords[unmunch_word[:-5]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[1:-5]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[2:-5]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[3:-5]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[4:-5]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[5:-5]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[6:-5]].add(unmunch_word)

    # unmunch_subwords[unmunch_word[:-6]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[1:-6]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[2:-6]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[3:-6]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[4:-6]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[5:-6]].add(unmunch_word)
    # unmunch_subwords[unmunch_word[6:-6]].add(unmunch_word)

print("len of unmunch_subwords:")
print(repr(len(unmunch_subwords)))

print(repr(unmunch_subwords["musí"]))

# this basically gets valid words related to the user dict
words_in_unmunch_that_have_userwords_as_substrings = set()

for userword_longer_than_5_word in subwords_in_userwords_longer_than_5:
    if userword_longer_than_5_word in unmunch_subwords:
        for orig_unmunch_word in unmunch_subwords[userword_longer_than_5_word]:
            words_in_unmunch_that_have_userwords_as_substrings.add(orig_unmunch_word)

print("len of words_in_unmunch_that_have_userwords_as_substrings:")
print(repr(len(words_in_unmunch_that_have_userwords_as_substrings)))

print(repr(sorted(words_in_unmunch_that_have_userwords_as_substrings)[123]))

# this basically gets valid words related to the other comm dict
words_in_unmunch_that_have_othercomm_words_as_substrings = set()

for othercomm_longer_than_5_word in subwords_in_othercomm_longer_than_5:
    if othercomm_longer_than_5_word in unmunch_subwords:
        for orig_unmunch_word in unmunch_subwords[othercomm_longer_than_5_word]:
            words_in_unmunch_that_have_othercomm_words_as_substrings.add(orig_unmunch_word)

print("len of words_in_unmunch_that_have_othercomm_words_as_substrings:")
print(repr(len( words_in_unmunch_that_have_othercomm_words_as_substrings)))

#print(repr(sorted( words_in_unmunch_that_have_othercomm_words_as_substrings)[123]))
print(repr(sorted( words_in_unmunch_that_have_othercomm_words_as_substrings)[0]))


# merging
# merge valid words from user dictionary
for word in words_in_both_userwords_unmunch:
    add_to_output_dict_if_not_there(word, 120)

# merge related valid words from user dictionary
for word in words_in_unmunch_that_have_userwords_as_substrings:
    add_to_output_dict_if_not_there(word, 100)

# merge valid words from other comm dictionary
for word in words_in_both_othercomm_unmunch :
    add_to_output_dict_if_not_there(word, 80)

# merge related valid words from other comm dictionary
for word in words_in_unmunch_that_have_othercomm_words_as_substrings:
    add_to_output_dict_if_not_there(word, 60)

# merge related valid words from the unmunch dict (in the order of frequency in the orig aosp dict)
for word, freq in anysoftkeyboard_orig.items():
    if word in unmunch_subwords:
        for related_unmunch_word in unmunch_subwords[word]:
            add_to_output_dict_if_not_there(related_unmunch_word, max(5, freq - 15))

    if word[:-1] in unmunch_subwords:
        for related_unmunch_word in unmunch_subwords[word[:-1]]:
            add_to_output_dict_if_not_there(related_unmunch_word, max(5, freq - 16))

    # TODO enable or disable?
    if word[:-2] in unmunch_subwords:
        for related_unmunch_word in unmunch_subwords[word[:-2]]:
            add_to_output_dict_if_not_there(related_unmunch_word, max(5, freq - 17))

    # TODO enable or disable?
    if word[:-3] in unmunch_subwords:
        for related_unmunch_word in unmunch_subwords[word[:-3]]:
            add_to_output_dict_if_not_there(related_unmunch_word, max(2, freq - 18))

    if word[1:] in unmunch_subwords:
        for related_unmunch_word in unmunch_subwords[word[1:]]:
            add_to_output_dict_if_not_there(related_unmunch_word, max(2, freq - 19))

    # TODO enable or disable?
    if word[2:] in unmunch_subwords:
        for related_unmunch_word in unmunch_subwords[word[2:]]:
            add_to_output_dict_if_not_there(related_unmunch_word, max(2, freq - 20))

    # TODO enable or disable?
    if word[3:] in unmunch_subwords:
        for related_unmunch_word in unmunch_subwords[word[3:]]:
            add_to_output_dict_if_not_there(related_unmunch_word, max(2, freq - 21))

    if word[1:-1] in unmunch_subwords:
        for related_unmunch_word in unmunch_subwords[word[1:-1]]:
            add_to_output_dict_if_not_there(related_unmunch_word, max(2, freq - 22))

    # TODO enable or disable?
    if word[2:-1] in unmunch_subwords:
        for related_unmunch_word in unmunch_subwords[word[2:-1]]:
            add_to_output_dict_if_not_there(related_unmunch_word, max(2, freq - 23))

    # if word[3:-1] in unmunch_subwords:
    #     for related_unmunch_word in unmunch_subwords[word[3:-1]]:
    #         add_to_output_dict_if_not_there(related_unmunch_word, max(2, freq - 24))

    # TODO enable or disable?
    if word[1:-2] in unmunch_subwords:
        for related_unmunch_word in unmunch_subwords[word[1:-2]]:
            add_to_output_dict_if_not_there(related_unmunch_word, max(2, freq - 25))

    # if word[2:-2] in unmunch_subwords:
    #     for related_unmunch_word in unmunch_subwords[word[2:-2]]:
    #         add_to_output_dict_if_not_there(related_unmunch_word, max(2, freq - 26))

    # if word[3:-2] in unmunch_subwords:
    #     for related_unmunch_word in unmunch_subwords[word[3:-2]]:
    #         add_to_output_dict_if_not_there(related_unmunch_word, max(2, freq - 27))

    # if word[1:-3] in unmunch_subwords:
    #     for related_unmunch_word in unmunch_subwords[word[1:-3]]:
    #         add_to_output_dict_if_not_there(related_unmunch_word, max(2, freq - 28))

    # if word[2:-3] in unmunch_subwords:
    #     for related_unmunch_word in unmunch_subwords[word[2:-3]]:
    #         add_to_output_dict_if_not_there(related_unmunch_word, max(2, freq - 29))

    # if word[3:-3] in unmunch_subwords:
    #     for related_unmunch_word in unmunch_subwords[word[3:-3]]:
    #         add_to_output_dict_if_not_there(related_unmunch_word, max(2, freq - 30))

# # merge the remaining unmunch dict words
# for word in unmunch:
#     add_to_output_dict_if_not_there(word, 3)


# preparation of the anysoftkeyboard dictionary
words_already_added_to_output_lines = set()
output_anysoft_dict_lines = [
    "dictionary=main:cs,locale=cs,description=Čeština,date=1393228135,version=45",
]
# freq : list[line, line, line, ...]
output_anysoft_dict_lines_by_freq = defaultdict(list)
for count in range(anysoftkeyboard_orig_order_counter):
    word = anysoftkeyboard_orig_order[count]
    freq = anysoftkeyboard_orig[word]
    line = " word={0},f={1},flags=,originalFreq={1}".format(word, str(freq))
    output_anysoft_dict_lines_by_freq[freq].append(line)
    words_already_added_to_output_lines.add(word)
for word in sorted(anysoftkeyboard_new.keys()):
    freq = anysoftkeyboard_new[word]
    if word in words_already_added_to_output_lines:
        continue
    line = " word={0},f={1},flags=,originalFreq={1}".format(word, str(freq))
    output_anysoft_dict_lines_by_freq[freq].append(line)
    words_already_added_to_output_lines.add(word)
for freq in sorted(output_anysoft_dict_lines_by_freq.keys(), reverse=True):
    for line in output_anysoft_dict_lines_by_freq[freq]:
        output_anysoft_dict_lines.append(line)

# this is the dictionary that should be packaged into the .apk for anysoftkeyboard
with open('output_anysoftkeyboard_cs_wordlist_huge_02.txt', 'w') as f:
    for line in output_anysoft_dict_lines:
        f.write(line + "\n")

words_only_in_userwords = words_only_in_userwords.difference(words_already_added_to_output_lines)

# these are only the non-valid words from user dict
# these should be added back to the android's user dict
# (these don't belong to the keyboard's built-in dictionary)
# later, filter out english words using this:
# cat output_words_only_in_userwords_01.txt | grep -v -Fx -f /usr/share/dict/words 
with open('output_words_only_in_userwords_01.txt', 'w') as f:
    for word in words_only_in_userwords:
        f.write(word + "\n")

print("the program reached the end")



# with open('userwords_02_related_unmunch_words_01.txt', 'w') as f:
#     for related_unmunch_word in words_in_unmunch_that_have_userwords_as_substrings:
#         f.write(related_unmunch_word + "\n")
#
#
# with open('words_only_in_unmunch_01.txt', 'w') as f:
#     for word in words_only_in_unmunch:
#         f.write(word + "\n")
#
# with open('words_in_both_01.txt', 'w') as f:
#     for word in words_in_both_userwords_unmunch:
#         f.write(word + "\n")
