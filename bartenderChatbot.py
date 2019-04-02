from flask import Flask, render_template, request, jsonify
from textblob import TextBlob
from spell import corection
import random
#import json
import os

os.environ['NLTK_DATA'] = '~/nltk_data'
GREETING_KEYWORDS = ("hello", "hi", "greetings", "sup", "what's up", "hi there", "good evening", "wuzzup my homie")
GREETING_RESPONSES = ["What can I get you?", "Hello stranger, what can I serve up for you?", "Need a drink?", "Hi, hope you're thirsty. What can I get you?"]
GOODBYE_KEYWORDS = ("bye", "good bye", "goodbye", "see ya")
GOODBYE_RESPONSES = ["Have a good night", "Drive safe!", "Until next time"]
HEDGE_RESPONSES = ["I have no idea what you're asking", "I'm not sure", "Can you re-phrase that?", "Pardon?", "Sorry I can't do that", "I'm confused"]
DRINKS = ("vodka", "beer", "whiskey", "wine", "sex on the beach", "screwdriver", "green fairy", "whiskey", "absinthe", "acapulco gold", "amaretto", "bacardi", "baileys" "budweiser", "champagne", "daiquiri", "goldschlager" "guinness", "grey goose", "hootch", "jack daniels", "jagermeister", "limoncello", "mezcal", "moonshine", "pina colada", "tequila", "vodka", "zinfandel", "raki", "long island iced tea"  )
DRINKSTYLE = ("on the rocks", "neat")#ask this after they request a drink
YES_KEYWORDS = ("yes", "yeah", "certainly", "true", "yep", "yea", "okay", "exactly", "gladly")
YES_RESPONSES = ["Okay", "Sounds good", "I like it", "Thats great!", "Exciting!"]
NO_KEYWORDS = ("no", "nah", "negative", "not really", "never", "false", "nope")
NO_RESPONSES = ["That's too bad", "Suit yourself", "If you say so", "I insist"]
chat_log = {}


def createMessage(input):
    '''Takes json facebook input and creates the message to return to facebook'''
    #input_msg = TextBlob(input['text'])
    spell_checked_word = correction(input)
    input_msg = TextBlob(spell_checked_word)
    #senderId = input['sid']
    senderId = 0
    data = buildMessage(input_msg, senderId) 
    #print(chat_log)
    return str(data)  #this will return the wanted message back out to messenger


def buildMessage(input_msg, senderId):
    '''Core Logic to build the message.
    If unsure how to reply, will respond with a hedge'''

    # Clears the user session to start over new
    if input_msg.lower() == 'clear':
        clearSession(senderId)
        return "Session cleared"

    times_con = howManyMessages(senderId)
    # If the user is greeting, respond with a greeting
    if CheckForGreeting(input_msg):
        return random.choice(GREETING_RESPONSES)

    # If the user is greeting, respond with a greeting
    if CheckForGoodbye(input_msg):
        # They're leaving, so clear the session
        clearSession(senderId)
        return random.choice(GOODBYE_RESPONSES)

    # Break the message into parts
    pronoun, noun, adjective, verb = getSpeechParts(input_msg)
    num_drinks = chat_log[senderId]['drinks_served']

    # Search for a drink in the user input and respond as well as we can
    drink = noun
    if noun not in DRINKS:
        drink = searchForDrink(input_msg)
    if len(input_msg.words) == 1:
        drink = input_msg
    if drink in DRINKS:
        if num_drinks > 3:
            return "You are too drunk I am unable to serve you any more drinks. You can type 'clear' to tell me that you're sober again"
        #increment drink counter
        chat_log[senderId]['drinks_served'] = num_drinks + 1
        if num_drinks <= 1:
            return "One {0} coming right up!".format(drink)
        if num_drinks == 2:
            return "{0} for you, enjoy.".format(drink)
        else:
            return "Here is your {0}! Wow you've already had {1} drinks!".format(drink, num_drinks)

    # Look for yes or no responses and respond with a weak hedge
    if checkForYes(input_msg):
        return random.choice(YES_RESPONSES)
    if checkForNo(input_msg):
        return random.choice(NO_RESPONSES)

    # If someone doesn't want anything
    if noun == "nothing":
        return "There isn't anything I can get for you? I am a master bar tender. You won't find any better."

    #If we have a noun but no drink, we don't know what they want, so we answer with a question
    if noun:
        resp = []
        if pronoun:
            print("pron" + pronoun)
            resp.append(pronoun)
        if verb:
            v = verb[0]
            if v is not None:
                resp.append(v)
        if startsWithVowel(noun):
            noun_pronoun = "an"
        else:
            noun_pronoun = "a"
        resp.append(noun_pronoun + " " + noun + "?")
        print(resp)
        return " ".join(resp)
    #If nothing caught, return a hedge
    return random.choice(HEDGE_RESPONSES)


def createChatLog(senderId):
    '''Keeps track of each session ID in a dictionary'''
    log = {'times_contacted': 1, 'context': None, 'drinks_served': 0}
    chat_log[senderId] = log


def howManyMessages(senderId):
    '''Check the chat log for number of messages and increment accordinly.'''
    if senderId not in chat_log:
        createChatLog(senderId)
        #return value is number of messages received
        return 1
    else:
        times_con = chat_log[senderId]['times_contacted'] + 1
        chat_log[senderId]['times_contacted'] = times_con
        return times_con


def clearSession(senderId):
    '''Delete any data from the user session log'''
    chat_log[senderId]['times_contacted'] = 0
    chat_log[senderId]['drinks_served'] = 0


def CheckForGreeting(sentence):
    '''Return boolean if the user sentence contains a greeting'''
    for word in sentence.words:
        if word.lower() in GREETING_KEYWORDS:
            return True
    return False


def CheckForGoodbye(sentence):
    '''Return boolean if the user wants to leave/end the sesion'''
    for word in sentence.words:
        if word.lower() in GOODBYE_KEYWORDS:
            return True
    return False


def checkForYes(sentence):
    '''Return boolean if the user indicated a yes/true reply'''
    for word in sentence.words:
        if word.lower() in YES_KEYWORDS:
            return True
    return False


def checkForNo(sentence):
    '''Return boolean if the user indicated a no/false reply'''
    for word in sentence.words:
        if word.lower() in NO_KEYWORDS:
            return True
    return False


def searchForDrink(sentence):
    '''Return boolean if the user sentence contains a drink'''
    for word in sentence.words:
        if word.lower() in DRINKS:
            return word
    return None


def getSpeechParts(input_msg):
    '''Use natural language processing to find and categorize each part of the sentance'''
    pronoun = None
    noun = None
    adjective = None
    verb = None
    for s in input_msg.sentences:
        pronoun = findPronoun(s)
        noun = findNoun(s)
        adjective = findAdjective(s)
        verb = findVerb(s)
    return pronoun, noun, adjective, verb


def findPronoun(sent):
    '''Return pronoun (I or You). Determins if the user is talking about
    themselves or the bot.
    Pronoun is represented as PRP in NLTK'''
    pronoun = None
    for word, part_of_speech in sent.pos_tags:
        if part_of_speech == 'PRP' and word.lower() == 'you':
            pronoun = 'I'
        elif part_of_speech == 'PRP' and word == 'I' or word == 'i':
            pronoun = 'You'
    return pronoun


def findVerb(sent):
    '''Return verb represended as VB in NLTK'''
    verb = None
    pos = None
    for word, part_of_speech in sent.pos_tags:
        if part_of_speech.startswith('VB'):  # This is a verb
            verb = word
            pos = part_of_speech
            break
    return verb, pos


def findNoun(sent):
    '''Return noun represended as NN in NLTK'''
    noun = None
    if not noun:
        for w, p in sent.pos_tags:
            if p == 'NN' and w != 'i':  # This is a noun
                #textblob detecting 'i' as a noun
                noun = w
                break
    return noun


def findAdjective(sent):
    '''Return adjective represended as JJ in NLTK'''
    adj = None
    for w, p in sent.pos_tags:
        if p == 'JJ':  # This is an adjective
            adj = w
            break
    return adj


def startsWithVowel(word):
    '''Used to check if a noun starts with a vowel
    then we can assign the proper pronoun'''
    return True if word[0] in 'aeiou' else False


#all code above this created API
app = Flask(__name__) #create the app server to recieve json
@app.route("/")
def root():
    return render_template('chat.html')

@app.route("/chat", methods=['POST','GET'])
def chat():
    content = str(request.form['chatmessage'])
    if content == "quit":
        exit()
        return jsonify({"status":"ok", "answer":"exit Thank You"})
    else:
        message = createMessage(content)
        return jsonify({'status':'OK','answer':message})

#@app.route('/givenMessage', methods = ['POST'])
#def postJsonHandler():
#    '''Receives POST request from webhook and returns POST data'''
#    #print (request.is_json)
#    content = request.get_json()
#    #print (content)
#    message = createMessage(content)
#    return message

app.run(host = '127.0.0.1', port = 8090)
