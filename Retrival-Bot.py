'''
If you choose to build a retrieval-based chatbot, we want to see the following:

You’ve implemented natural language processing and machine learning techniques, including a language or topic model like Bag-of-Words or tf-idf and word embeddings using word2vec.
You’ve included a closed-domain chatbot architecture that encompasses:
- intent classification
- entity recognition
- response selection
'''

#preprocessing text
import random
import re
from collections import Counter
from urllib import response
import spacy
from nltk import pos_tag
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords


#loads in a vectorizer to anylize words and compare them to make the best match
word2vec = spacy.load('en_core_web_sm')
#loads in stop words to speed up the proccessing
stopWords = set(stopwords.words('english'))

#preprocessing text and del stopwords
def preproccess(input_sentence):
    input_sentence = input_sentence.lower()
    input_sentence = re.sub(r'[^\w\s]', '', input_sentence)
    tokens = word_tokenize(input_sentence)
    input_sentence = [i for i in tokens if i not in stopWords]
    return input_sentence

#prepare list of nouns
def extractNouns(userMessage):
    message_nouns = []
    postTagMessage = pos_tag(preproccess(userMessage))
    for word in postTagMessage:
        if word[1].startswith('N'):
            message_nouns.append(word[0])
    return message_nouns


#count how many words from user reply are in possible response
def compareOverlap(user_message, possible_response):
    similar_words = 0
    for word in user_message:
        if word in possible_response:
            similar_words += 1
    return similar_words

#compares nouns to each other in order to select the correct one for the blank spot
def computeSimilarity(tokens, category):
    outputList = []
    tokenVec = word2vec(" ".join(tokens))
    catVec = word2vec(category)
    for token in tokenVec:
        outputList.append([token.text, catVec.text, token.similarity(catVec)])
    outputList.sort(key=lambda x : x[2])
    if outputList:
        return outputList[-1][0]
    else:
        return category
#reservations list
oldDict = {
    0: ["Day", "Hours", "Menu"],
    1: ["Monday", "18:30", "Lunch"],
    2: ["Tuesday", "12:30", "Breakfast"],
}
#days
daysOfWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
#menu
menu = ['Breakfast', 'Lunch', 'Dinner']

#makes a random number for the customer ID inbetween 0-30
def getId():
    orderId = random.randint(0, 30)
    return orderId

def proccessBooking(info):
    bookingId = getId()
    for key in oldDict.keys():
        if key == bookingId:
            return proccessBooking(info)
    oldDict[bookingId] = info
    return bookingId

class ChatBot():
    def __init__(self):
        #defaut ID for teh same reason
        self.id_ = "0"
        #default name for the same reason
        self.name = "null"
        #list of negative words (the spaces are to prevent double matches in a for loop)
        self.negativeWords = [" go away ", " leave ", " nothing ", " stop ", " exit ", " no ", " bye ", " good bye ", " quit ", " nope "]
        #list of positive words
        self.positiveWords = [" yes ", " yea ", " yeah ", " yep ", " correct ", " ye ", " y "]
        #these are the replies for the retrieval based part of the chatbot
        self.posResponses = ["If you are running late your table will still be available 15 minutes after your booked time.", "I\'m OK too :)", "Don't worry about traffic jams, your reservation will be available 15 minutes after your booked time.", "The {0} menu you have chosen does not contain allergens", "We do not serve take-away meals"]
        #posible routes for the rule based ordering 
        self.posRoutes = {
            "reservation": [r'.*change.*(reserve)?', r'.*reschedule.*(reserve)?'],
            "table": [r'.*reserv.*', r'.*table.*', r'.*book.*'],
            "info": [r'.*info.*']
        }
        #the noun that it matches to 
        self.blankSpot = "restaurant"
        
    def make_exit(self, user_input):
        for token in self.negativeWords:
            if token.strip() in user_input:
                print(f'Goodbye, see you next time!')
                return True

    def chat(self):
        #new customer
        self.name = input('Hello in ¡ojo! restaurant! I\'m Pablito, may I please have your name? \n>>')
        output = input(f"Hello {self.name}. Do you already have a reservation ID? \n>> ")
        #check that reply is positive
        for word in self.positiveWords:
            if word.strip() in output.lower():
                #get id for user
                self.id_ = input("Awesome! What is it? \n>> ")
                try:
                    print(f'Great, you have reserved a table for {oldDict[int(self.id_)][0]} at {oldDict[int(self.id_)][1]} and you chosen a {oldDict[int(self.id_)][2]} menu.')
                    output = input(f"What can I do for you {self.name}? \n>> ")
                except KeyError:
                    print("Sorry that reservation ID doesn't exist please try again.")
                    return self.chat()
                #this ensres that they did not use a negative escape word and if they didn't it proccesses their response
                return self.convController(output)
            else:
                output = input(f"How may I help you today {self.name}? \n>> ")
                #this ensres that they did not use a negative escape word and if they didn't it proccesses their response
                return self.convController(output)
    #controller
    def convController(self, user_input):
        for key, val in self.posRoutes.items():
            for word in val:
                checkRout = re.match(word, user_input.lower())
                if checkRout and key == 'reservation':
                    return self.changeReservation()
                elif checkRout and key == "table":
                    return self.handleTable()
                elif checkRout and key == "info":
                    print(f'You have reserved a table for {oldDict[int(self.id_)][0]} at {oldDict[int(self.id_)][1]} and you chosen a {oldDict[int(self.id_)][2]} menu.')
                    output = input(f"Is there anything else I can do for you {self.name}? \n>> ")
                    return self.continueConvo(output)
        
        return self.handleReply(user_input) 

    #change reservation
    def changeReservation(self):
        try:
            output = input("Enter date of new reservation. (day, hour:minutes) \n>>").capitalize()
            dayHours = re.split(r',?\s', output)
            patternMatch = re.match(r'\d\d:\d\d', dayHours[1])
            if dayHours[0] in daysOfWeek and patternMatch:
                oldDict[int(self.id_)][0] = dayHours[0].capitalize()
                oldDict[int(self.id_)][1] = dayHours[1]
                print(f"You have changed your reservation to {oldDict[int(self.id_)][0]} {oldDict[int(self.id_)][1]}.")
                print(f"Just to remaind you chosen a {oldDict[int(self.id_)][2]} menu.")
            else:
                print("Sorry, use pattern (Day, Hour:Minutes)")
                return self.changeReservation()
        except Exception:
            print("Sorry, use pattern (Day, Hour:Minutes)")
            return self.changeReservation()

        output = input(f'Is there anything else I can help you with {self.name}? \n>>')
        return self.continueConvo(output)
    
    #reserve table
    def handleTable(self):
        info = []
        while True:
            output = input('Great, on which day would you like to visit our restaurant? \n>>').capitalize()
            if output in daysOfWeek:
                info.append(output)
                break
        while True:
            output2 = input('What time would you like to reserve a table? (hour:minutes) \n>>')
            if re.match(r'\d\d:\d\d', output2):
                info.append(output2)
                break
        while True:
            output3 = input('What menu do you prefer? Breakfast, Lunch, Dinner? \n>>').capitalize()
            if output3 in menu:
                info.append(output3)
                break
        self.id_ = proccessBooking(info)
        print(f"Your reservatiom ID is {self.id_}. It is important that you remember this as it is how you can access information.")
        output4 = input(f"Is there anything else I can do for you {self.name}? \n>> ")
        return self.continueConvo(output4)

    #does the whole retrieval based part 
    def handleReply(self, user_input):
        #gets the correct response based on the word similarity
        intent = self.getIntent(user_input)
        #gets the noun from the reply
        entity = self.getEntity(user_input)
        #this is important because it helps the reply if you have an order already make more sense
        if intent in self.posResponses:
            print(intent)
        else:
            print(f"Sorry, I don't understand what you mean by saying {entity}")
        output = input("Is there anything else I can help you with? \n>>")
        #and now we do it all over again fun stuff!
        return self.continueConvo(output)

    def continueConvo(self, reply):
        #checks the reply against words in negative words
        for word in self.negativeWords:
            if word.strip() in reply.lower():
                #if they want to leave it exits with a message saying goodbye
                return print(f"Goodbye {self.name}.") 
        #other wise it sents it to the convocontroller 
        return self.convController(reply)
    #get most matching response
    def getIntent(self, user_input):
        bow_usuer_input = Counter(preproccess(user_input))
        responsesCounted = [Counter(preproccess(response)) for response in self.posResponses]
        similarity_list = [compareOverlap(bow_usuer_input, words)for words in responsesCounted]
        responseIndex = similarity_list.index(max(similarity_list))
        return self.posResponses[responseIndex]
    #get noun from user input
    def getEntity(self, user_input):
        nouns = extractNouns(user_input)
        noun = computeSimilarity(nouns, self.blankSpot)
        return noun



a = ChatBot()
a.chat()