# Software-Eng-Chatbot
## 310 Assignment 3: CHAT BOT MODIFICATIONS
## USER GUIDE
Aaron Mahnic,
Ansa Erturk,
Mishal Hasan,
Raphael Chevallier,
Tyrel Narciso
## Individual Assignment by: Tyrel Narciso

## Introduction
For this assignment, we built a chat bot to mimic basic bartending needs. Initially built with basic drink request functionality, the bot has been modified to receive basic feedback on their time at the bar from the customer. The bartender will also serve meals taken from his MEALS database as well as drinks, amongst other changes such as spell checking and synonym checking.


## Infrastructure
The bartender chatbot uses a simple gui alternative to face as a front-end. which is still done through a nodeJS webhook that passes the message data to a python service (flask) which processes the user's message and responds accordingly. The gui is now hosted on the computer of the user alone now, it cannot be accessed online. The flask chatbot bartenderChatbot.py can run as a stand-alone chatbot service and hook into any kind of front end interface with minimal changes. Chat flow when user messages the bot follows the steps below.
* User activates bartenderChatbot.py
* User holds CRTL and clicks on the url the file is "Running on"
* Input into gui is performed
* Node JS
* Flask chatbot receives message and the reply is taken back up the chain

## Libraries
* NLTK/TextBlob (tokenize, tag, Word, TextBlob) - Python framework used for natural language processing
* Flask - Python web framework used to communicate with POST requests
* Random - random number generator

## Gain Permission to Access Chatbot
Originally permission was more difficult to attain for the facebook version. This local version however simply needs the proper dependencies on the host computer and the proper steps followed.

## Potential Improvements
Although the system’s functionality is efficient as a basic bot, it can be improved by adding data outside the context of a bar and by populating the existing categories (eg. drinks). More elaborate methods can be added to detect false positives after an advanced contextual recognition algorithm is implemented. 

# Install Chatbot to own server
## Prerequisites
* NodeJS
* Python 3
* Flask

## Installing
Example commands for installing the Chatbot on an Ubuntu or Debian server. Flask can be installed using pip. It would be good practice to use a python virtualenv if installing on a shared computer.
```console
user@server:~$ apt install nodejs 
user@server:~$ apt install npm
user@server:~$ apt install python3-pip
user@server:~$ pip3 install flask
user@server:~$ apt install git
user@server:~$ git clone https://github.com/TyrelN/Bartender-Chatbot
user@server:~$ cd Bartender-Chatbot/
user@server:~$ npm install
```
## Running
Once installed, run flask and node as background processes.
```console
user@server:~$ node webhook.js &
user@server:~$ python3 bartenderChatbot.py &
```
Run the py file and access the url in a browser:
'''console
 * Serving Flask app "bartenderChatbot" (lazy loading)
 * Environment: production
   WARNING: Do not use the development server in a production environment.uction environment.
   Use a production WSGI server instead.
 * Debug mode: off                                      it)
 * Running on http://127.0.0.1:8090/ (Press CTRL+C to quuit)  
 '''
 ##Features 
