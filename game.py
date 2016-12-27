import telebot
import random
from collections import Counter

bot = telebot.TeleBot("200009247:AAHf6MAz5e3NOWr0Ypb_vnWhGiKuOrz8Fcg")
# Handles all text messages that contains the commands '/start' or '/help'.
d = open('diction.dictionary')
dictionaryItems = d.read().split("\n")
bigwords = []
for items in dictionaryItems:
    if len(items) == 9:
        bigwords.append(items)


def combinations(string):
    yield ''
    for i, d in enumerate(string):
        for comb in combinations(string[i + 1:]):
            yield d + comb

            # Takes a list as input and outputs only the words in dictionary


def dictletters(words):
    a = []
    for item in words:
        if item in dictionaryItems and len(item)>2:
            a.append(item)
    return a

# storing it in dictionary so tht scoring can be easy based on the number of letters they could conjure


def possible(ourword):
    allpossible = {}
    word = ""
    for letter in ourword:
        word = word + letter
        b = dictletters(combinations(word))
        for items in b:
            allpossible[items] = len(items)
    return allpossible


ourword = ""
alpossible = {}
letters={}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    ourword = ''.join(sorted(random.choice(bigwords)))
    bot.reply_to(message, "Howdy, Make as many words as possible with:" + ourword)
    #alpossible.update(possible(sorted(ourword)))
    #print(alpossible)
    letters.update(dict(Counter(ourword)))


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    a = str(message.text)
    a=a.lower()
    if a == "*" or a == "end-it":
        bot.reply_to(message, "GoodBye!!")
        pass
        return

    elif a not in alpossible:
        alpossible[a]=1
    else:
        alpossible[a]=alpossible[a]+1
    #print(letters)

    l2 = dict(Counter(a))
    #print(l2)
    flag = 0
    for keys, values in l2.items():
        if keys not in letters:
            flag=1
            break
        elif letters[keys] < values:
            flag = -1
            break
        else:
            continue


    if a not in dictionaryItems:
        flag=1
    if(flag!=0):
        if alpossible[a] >1:
            bot.reply_to(message, "You have given the same invalid input")
        else:
            bot.reply_to(message, "Invalid Input")
    else:
        if alpossible[a]>1:
            bot.reply_to(message, "Your have already entered this")
        elif a in alpossible:
            bot.reply_to(message, "Keep going")
        else:
            bot.reply_to(message, message.text + " is not a valid word")


bot.polling()
