from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
    got_request_exception,
)
from database.database_functions import (
    get_last_user_word,
    insert_into_user_words,
    get_user,
    insert_into_user_data,
    get_user_data,
    insert_into_logs,
)
import random

JWT_PAYLOAD = "jwt_payload"

bigwords = set()
dictionaryItems = []
with open("words.txt", "r") as f:
    dictionaryItems = set(f.read().lower().split("\n"))
    for items in dictionaryItems:
        if len(items) >=6:
            bigwords.add(items)


def get_freq(word):
    all_freq = dict()
    for i in word:
        if i in all_freq.keys():
            all_freq[i] += 1
        else:
            all_freq[i] = 1
    return all_freq


def get_new_word():
    return random.sample(bigwords, 1)[0]


def is_possible(og_word, word):
    print(og_word, word, "ISPOSSIBLE")
    if word.lower() in dictionaryItems:
        og_freq = get_freq(og_word)
        for ch, val in get_freq(word).items():
            if ch not in og_freq:
                return "invalid"
            if val > og_freq[ch]:
                return "invalid"
    else:
        return "not in dictionary"
    return "valid"


def shuffle_word(word):
    str_var = list(word)
    random.shuffle(str_var)
    return "  ".join(str_var)


def handle_commands(command):
    command = command.lower()
    print(command, "COMMAND")
    if command in ["/new", "/skip"]:
        new_word = get_new_word()
        insert_into_user_words(
            get_user(session[JWT_PAYLOAD]["name"])[0]["id"], new_word
        )
        new_word = shuffle_word(new_word)
        session["current_word"] = new_word
        return "Your new word is: " + new_word
    elif command == "/start":
        return """You will get a scrambelled word. Enter as many words as possible </br>Enter <b>/new</b> to get a new word.</br>Enter <b>/show</b> display your currernt word.</br>Enter <b>/shuffle</b> to suffle your current word.</br></br>You can enter a word one by one or seperated by comma."""
    elif command == "/shuffle":
        word = (
            session["current_word"]
            if "current_word" in session
            else get_last_user_word(get_user(session[JWT_PAYLOAD]["name"])[0]["id"])[0][
                "word"
            ]
        )
        word = shuffle_word(word)
        return "Your reshuffled word is " + word
    elif command == "/show":
        if "current_word" in session:
            return "Your current word is: " + session["current_word"]
        else:
            return get_last_user_word(get_user(session[JWT_PAYLOAD]["name"])[0]["id"])[
                0
            ]["word"]
    else:
        return "Wrong Command"


def get_user_words(email):
    data = get_user_data(get_user(email)[0]["id"])
    final_data = {}
    for user_word in data:
        if user_word["word"] in final_data:
            final_data[user_word["word"]] = (
                final_data[user_word["word"]] + ", " + user_word["input_word"]
            )
        else:
            final_data[user_word["word"]] = user_word["input_word"]
    return final_data


def conversation_log(func):
    """
    decorator to log conversations for a user
    :return: None
    """

    def wrapper(*args, **kwargs):
        if JWT_PAYLOAD in session and func.__name__ is not "send_text":
            insert_into_logs(session[JWT_PAYLOAD]["name"], request.form["text"])
        elif func.__name__ == "send_text":
            insert_into_logs(session[JWT_PAYLOAD]["name"], args[0], True)
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


@conversation_log
def send_text(text):
    return jsonify({"text": text})


def split_text(text):
    return text.lower().replace(" ", "").split(",")


def handle_input(message):
    try:
        if message.startswith("/"):
            return handle_commands(message)
        else:
            og_word = get_last_user_word(
                get_user(session[JWT_PAYLOAD]["name"])[0]["id"]
            )[0]["word"]
            bad_words = []
            for word in split_text(message):
                is_proper = is_possible(og_word, word)
                if is_proper == "valid":
                    insert_into_user_data(
                        get_user(session[JWT_PAYLOAD]["name"])[0]["id"], og_word, word
                    )
                else:
                    bad_words.append(word + " is " + is_proper)
            if bad_words:
                return "</br>".join(bad_words)
            else:
                return "Input word is valid"
    except Exception as e:
        return "Error " + str(e) + "</br>Try /start command to restart"


if __name__ == "__main__":
    print(get_user_words("ufoundashish@gmail.com"))
