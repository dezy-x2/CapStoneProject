import re
import spacy
from nltk.corpus import stopwords
from collections import Counter
from nltk import pos_tag
from nltk.tokenize import word_tokenize
import datetime
import random
import pickle

#loads in a vectorizer to anylize words and compare them to make the best match
word2vec = spacy.load('en_core_web_lg')
#loads in stop words to speed up the proccessing
stopWords = set(stopwords.words('english'))

#cleans up the replies to make them easier to anylize
def preproccess(given):
    loweredGiven = given.lower()
    cleanedGiven = re.sub(r'[^\w\s]', '', loweredGiven)
    tokenized = word_tokenize(cleanedGiven)
    product = [sentence for sentence in tokenized if sentence not in stopWords]
    return product

#picks the correct reply based on the amount of overlap between the reply and a response
def compareOverlap(userMessage, response):
    compareCounter = 0
    for word in userMessage:
        if word in response:
            compareCounter += 1
    return compareCounter

#picks out the nouns from a given sentence
def extractNouns(userMessage):
    nouns = []
    userMessageTagged = pos_tag(preproccess(userMessage))
    for item in userMessageTagged:
        if "NN" in item[1]:
            nouns.append(item[0])
    return nouns

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

#makes a random number for the customer ID inbetween 0-999
def getId():
    orderId = random.randint(0, 1000)
    return orderId

#this is where cusomer info is stored
orderDict = dict()
# print(orderDict[int("123")][0])

#does the actual action of storing the data in orderDict
def processOrder(info):
    orderId = getId()
    for ids in orderDict.keys():
        if ids == orderId:
            orderId = getId()

    orderDict[orderId] = info
    return orderId 

#this ones pretty obvious
daysOfWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
#gets the day of the week in numbers to be compared to the list right up there ^
dayOfWeek = datetime.datetime.today().weekday() - 5
# print(daysOfWeek[dayOfWeek])


#class where everything for the actuall chat bot is kept
class ChatBot:
    def __init__(self):
        #default dictionary incase anything goes wrong
        self.oldDict = {0: ["null", "order", "never"]}
        #defaut ID for teh same reason
        self.id_ = "0"
        #default name for the same reason
        self.name = "null"
        #list of negative words (the spaces are to prevent double matches in a for loop)
        self.negativeWords = [" go away ", " leave ", " nothing ", " stop ", " exit ", " no ", " bye ", " good bye ", " quit ", " nope "]
        #list of positive words
        self.positiveWords = [" yes ", " yea ", " yeah ", " yep ", " correct ", " ye ", " y "]
        #pretty self explanatory
        self.goodbyeMessage = "Sorry to see you go {}."
        #posible routes for the rule based ordering 
        self.posRoutes = {"order": [r'.*purchase.*', r'.*buy.*', r'.*get.*']}
        #these are the replies for the retrieval based part of the chatbot
        self.posResponses = ["Your order of {0} should be here by {1}.", "Our {0} sizes typically run large so I would order either your size or bigger.", "We have been selling {0} since 1999."]
        #the noun that it matches to 
        self.clothingBlank = "clothing"
    
    #main function that starts it all
    def handleGreet(self):
        #checks if they are a previous customer or not
        prevCustomer = input("Hi there! Do you already have a order ID? \n> ")
        #for loop to go through what they put down for a response
        for word in self.positiveWords:
            if word in prevCustomer.lower():
                #redeclares the ID
                self.id_ = input("Awesome! What is it? \n> ")
                #redecleares the oldDict with their previous info (pickle is a function that is able to hold over their data, unfortunately only able to hold one set for now)
                self.oldDict = pickle.load(open("orders", "rb"))
                #little try statement to avoid errors being thrown up as they aren't very human like
                try:
                    #redeclares the name
                    self.name = self.oldDict[int(self.id_)][0]
                    # print(self.oldDict)
                    output = input(f"Ok, what can I do for you {self.oldDict[int(self.id_)][0]}? \n> ")
                except KeyError:
                    print("Sorry that customer ID doesn't exist please try again.")
                    return
                #this ensres that they did not use a negative escape word and if they didn't it proccesses their response
                return self.continueConvo(output)
            else:
                #handles it if you are a new customer/don't have a current order ID
                self.name = input("Hello there can I please have your name? \n> ")
                output = input(f"Hello there {self.name} how may I help you today? \n> ")
                #this ensres that they did not use a negative escape word and if they didn't it proccesses their response
                return self.continueConvo(output)
    
    #used for the rule based search and otherwise sets it off to retrieval based 
    def convoController(self, reply):
        for key, value, in self.posRoutes.items():
            for option in value:
                foundMatch = re.match(option, reply.lower())
                if foundMatch and key == "order":
                    return self.handleOrder(reply)
        
        return self.handleReply(reply) 
    
    #does what the name says it does
    def handleOrder(self, reply):
        #determines the noun aka what they are planning on ordering
        noun = self.determineEntity(reply)
        #double checks that it was correct
        output = input(f"Am I correct that you wish to purchase a {noun}? \n> ")
        #looks at the response to make sure that it was correct
        for word in self.positiveWords:
            if word in output.lower():
                #proccesses the order
                orderId = processOrder([self.name, noun, daysOfWeek[dayOfWeek]])
                #"pickles" the data
                pickle.dump(orderDict, open("orders", "wb"))
                # print(orderDict)
                #tells them their order ID
                print(f"Your order ID is {orderId}. It is important that you remember this as it is how you can access information about you order later.")
                #because its so polite it asks them if theres anything else it can do for them
                output2 = input(f"Is there anything else I can do for you {self.name}? \n> ")
                #this ensres that they did not use a negative escape word and if they didn't it proccesses their response
                return self.continueConvo(output2)
            else:
                #uh oh looks like I messed up time to try again
                print("Sorry, lets try that again.")
                output3 = input(f"How can I help you {self.name}? \n> ")
                #this ensres that they did not use a negative escape word and if they didn't it proccesses their response
                return self.continueConvo(output3)
    #picks the reply out
    def determineIntent(self, reply):
        #uses the preproccess function and turns it into a BoW (bag of words)
        replyCounted = Counter(preproccess(reply))
        #does the same thing for the replies
        responsesCounted = [Counter(preproccess(response)) for response in self.posResponses]
        #compiles a list of what reply is most similar through magic
        simList = [compareOverlap(replyCounted, response) for response in responsesCounted]
        #sorts the list and gets the best ones index
        idx = simList.index(max(simList))
        #returns the correct response
        return self.posResponses[idx]
    
    #determines the correct noun to use
    def determineEntity(self, reply):
        #gets the nouns from the reply
        nounList = extractNouns(reply)
        #gets the correct noun
        noun = computeSimilarity(nounList, self.clothingBlank)
        return noun
    
    #this is the fun function that determines whether or not to keep talking
    def continueConvo(self, reply):
        #checks the reply against words in negative words
        for word in self.negativeWords:
            if word in reply.lower():
                #if they want to leave it exits with a message saying goodbye
                return print(self.goodbyeMessage.format(self.name)) 
        #other wise it sents it to the convocontroller 
        return self.convoController(reply)
    
    #does the whole retrieval based part 
    def handleReply(self, reply):
        #gets the correct response based on the word similarity
        intent = self.determineIntent(reply)
        #gets the noun from the reply
        entity = self.determineEntity(reply)
        #this is important because it helps the reply if you have an order already make more sense
        if intent == self.posResponses[0]:
            print(intent.format(self.oldDict[int(self.id_)][1], self.oldDict[int(self.id_)][2]))
        else:
            print(intent.format(entity))
        output = input("Is there anything else I can help you with? \n> ")
        #and now we do it all over again fun stuff!
        return self.continueConvo(output)

# print(orderDict)
chatter = ChatBot()
chatter.handleGreet()