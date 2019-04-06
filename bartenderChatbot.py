from flask import Flask, render_template, request, jsonify
from textblob import TextBlob
from textblob import Word
from spell import correction, words, candidates
import random
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
#import json
import os
#synonym checking implemented
#sentiment analysis implemented 
#POS tagging implemented - synergizes with sentiment analysis
#REFERENCES: https://stevenloria.com/wordnet-tutorial/
#https://medium.com/@gianpaul.r/tokenization-and-parts-of-speech-pos-tagging-in-pythons-nltk-library-2d30f70af13b
#https://www.geeksforgeeks.org/part-speech-tagging-stop-words-using-nltk-python/
#https://www.geeksforgeeks.org/twitter-sentiment-analysis-using-python/

os.environ['NLTK_DATA'] = '~/nltk_data'
GREETING_KEYWORDS = ("yo", "hey", "hello", "hi", "greetings", "sup", "what's up", "hi there", "good evening", "wuzzup my homie")
GREETING_RESPONSES = ["What can I get you?", "Hello stranger, what can I serve up for you?", "Hey there! Need a drink?", "Hi, hope you're thirsty. What can I get you?", "Welcome! What'll it be today?"]
GOODBYE_KEYWORDS = ("bye", "good bye", "goodbye", "see ya")
GOODBYE_RESPONSES = ["Have a good night", "Drive safe!", "Until next time"]
MEALS = ["steak", "hamburger", "fish and chips", "blt", "spaghetti", "hot dog", ]
HEDGE_RESPONSES = ["I have no idea what you're asking", "I'm not sure", "Can you re-phrase that?", "Pardon?", "Sorry I can't do that", "I'm confused"]
DRINKS = ("vodka", "beer", "whiskey", "wine", "sex on the beach", "screwdriver", "green fairy", "whiskey", "absinthe", "acapulco gold", "amaretto", "bacardi", "baileys" "budweiser", "champagne", "daiquiri", "goldschlager" "guinness", "grey goose", "hootch", "jack daniels", "jagermeister", "limoncello", "mezcal", "moonshine", "martini", "pina colada", "tequila", "vodka", "zinfandel", "raki", "long island iced tea"  )
DRINKSTYLE = ("on the rocks", "neat")#ask this after they request a drink
YES_KEYWORDS = ("good", "yes", "that's good", "yeah", "certainly", "true", "yep", "yea", "okay", "exactly", "gladly")
YES_RESPONSES = ["Okay", "Sounds good", "I like it", "Thats great!", "Exciting!"]
NO_KEYWORDS = ("no", "nah", "negative", "not really", "never", "false", "nope")
NO_RESPONSES = ["That's too bad", "Suit yourself", "If you say so", "I insist"]
chat_log = {}
GRATITUDE = ["thanks", "thank you", "much obliged", "thanks a bunch"]


#testing section for determining synonyms
#synonym tested words are: grub, alcohol, booze, nothing, dandy, goodbye, hello all at [0]
# testword = Word("milk")
# bev = testword.synsets[0]
print(candidates("grub"))
# print(bev.lemma_names())

def createMessage(input):
    '''Takes json facebook input and creates the message to return to facebook'''
    #input_msg = TextBlob(input['text'])
    
    spellingcheck = str(input).split()
    counter = 0
    for x in spellingcheck:
        
        if x not in candidates(x) and x not in Word("grub").synsets[0].lemma_names() and x not in Word("booze").synsets[0].lemma_names() and x not in MEALS and x not in DRINKS:
            spellingcheck[counter] = correction(x)
            print(spellingcheck[counter])
        counter += 1
    spell_checked_word = " ".join(spellingcheck)
    print(spell_checked_word)
    input_msg = TextBlob(spell_checked_word)
    #senderId = input['sid']
    senderId = 0
    data = buildMessage(input_msg, senderId) 
    #print(chat_log)
    return str(data)  #this will return the wanted message back out to messenger

def checkForFeedback(words): #for checking sentiment behind response
    analysis = TextBlob(str(words))
    if analysis.sentiment.polarity > 0:
        return 'positive'
    elif analysis.sentiment.polarity == 0:
        return 'neutral'
    else:
        return 'negative'

def buildMessage(input_msg, senderId):
    '''Core Logic to build the message.
    If unsure how to reply, will respond with a hedge'''
    tokenform = nltk.word_tokenize(str(input_msg)) #pos tagging form of sentence
    #initializes switch for feedback
    
    
    if tokenform[0] in GRATITUDE:
        return "You're welcome!"
   
    
        
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
        
        #the user will give an impression with their farewell which the bartender will respond to
        #setGoodByeTrue()
        if checkForFeedback(tokenform) == 'positive':
            clearSession(senderId)
            
            return "Happy to hear that!  " + random.choice(GOODBYE_RESPONSES)
        elif checkForFeedback(tokenform) == 'negative':
            clearSession(senderId)
            
            return "I'm sorry to hear that. " + random.choice(GOODBYE_RESPONSES)
        else:
            clearSession(senderId)
            
            return random.choice(GOODBYE_RESPONSES)
        
      

    # Break the message into parts
    pronoun, noun, adjective, verb = getSpeechParts(input_msg)
    num_drinks = chat_log[senderId]['drinks_served']

    # Search for a drink in the user input and respond as well as we can
    drink = noun #pass the noun through spell check 
    if noun not in DRINKS:
        drink = searchForDrink(input_msg)
    if len(input_msg.words) == 1:
        drink = input_msg
    if drink in DRINKS:
        if tokenform[0] == 'can' or tokenform[0] == 'may': #pos tagging to specify 
            return "you sure "+ tokenform[0] + "! here's your {0}".format(drink)
        if num_drinks == 1:
            
            return "Here's your {0}. How are you enjoying your drink so far?"
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
    if noun == Word("nothing").synsets[0].lemma_names():
        return "There isn't anything I can get for you? I have a vast knowledge of drinks. I'm sure you'll like something we have in stock."
    # If the noun is a meal: 
    meal = noun
    if noun not in MEALS:
        meal = searchForMeal(input_msg)
    if len(input_msg.words) == 1:
        meal = input_msg
    if meal in MEALS:
        if tokenform[0] == 'can' or tokenform[0] == 'may': #pos tagging to specify 
            return "you sure "+ tokenform[0] + "! here's your {0}".format(meal)
        if num_drinks == 1:
            
            return "Here's your {0}. How are you enjoying your food so far?".format(meal)
        else:
            return "Alright, here's your {0}, bon appetite".format(meal)
    #If we have a noun but no drink, we don't know what they want, so we answer with a question
    for x in tokenform: 
        print(str(x))
        if str(x) in Word("grub").synsets[0].lemma_names():
            return "Sounds good. What would you like to eat?"
    for x in tokenform:
        print(str(x))
        if str(x) == "drink" or x in Word("booze").synsets[0].lemma_names():
            return "One drink coming up. What's your fancy?"
    if noun:
        if checkForFeedback(tokenform) == 'positive':
            return "Happy to hear that!  "
        elif checkForFeedback(tokenform) == 'negative':
            return "Oh that's no good. I'm sure we can fix that"
        else:
            return "well, can't say I understood that, I'll assume it was positive!" 
    #If nothing caught, return a hedge
    return random.choice(HEDGE_RESPONSES)
#process if the passed sentence is positive negative or neutral
# def get_sentiment(processed_sentence):
#     analysis = TextBlob(processed_sentence)
#     if analysis.sentiment.polarity > 0:
#         return 'positive'
#     elif analysis.sentiment.polarity == 0:
#         return 'neutral'
#     else:
#         return 'negative'

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
        if word.lower() in GREETING_KEYWORDS or word.lower() in Word("hello").synsets[0].lemma_names():
            return True
    return False


def CheckForGoodbye(sentence):
    '''Return boolean if the user wants to leave/end the sesion'''
    for word in sentence.words:
        if word.lower() in GOODBYE_KEYWORDS or word.lower() in Word("goodbye").synsets[0].lemma_names():
            return True
    return False


def checkForYes(sentence):
    '''Return boolean if the user indicated a yes/true reply'''
    for word in sentence.words:
        if word.lower() in YES_KEYWORDS or word.lower() in Word("yes").synsets[0].lemma_names():
            return True
    return False


def checkForNo(sentence):
    '''Return boolean if the user indicated a no/false reply'''
    for word in sentence.words:
        if word.lower() in NO_KEYWORDS or word.lower() in Word("no").synsets[0].lemma_names():
            return True
    return False


def searchForDrink(sentence):
    '''Return boolean if the user sentence contains a drink'''
    for word in sentence.words:
        if word.lower() in DRINKS: #or word.lower in Word(word).synsets[0].lemma_names():
            return word
    return None

def searchForMeal(sentence):
    '''Return boolean if the user sentence contains a drink'''
    for word in sentence.words:
        if word.lower() in MEALS: # or word.lower in Word(word).synsets[0].lemma_names():
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
