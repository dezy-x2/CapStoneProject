import re
import spacy
from nltk.corpus import stopwords
from collections import Counter
from nltk import pos_tag
from nltk.tokenize import word_tokenize
import datetime
import random
import pickle

word2vec = spacy.load('en_core_web_lg')
stopWords = set(stopwords.words('english'))

def preproccess(given):
    loweredGiven = given.lower()
    cleanedGiven = re.sub(r'[^\w\s]', '', loweredGiven)
    tokenized = word_tokenize(cleanedGiven)
    product = [sentence for sentence in tokenized if sentence not in stopWords]
    return product

def compareOverlap(userMessage, response):
    compareCounter = 0
    for word in userMessage:
        if word in response:
            compareCounter += 1
    return compareCounter

def extractNouns(userMessage):
    nouns = []
    userMessageTagged = pos_tag(preproccess(userMessage))
    for item in userMessageTagged:
        if "NN" in item[1]:
            nouns.append(item[0])
    return nouns

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

def getId():
    orderId = random.randint(0, 1000)
    return orderId

orderDict = dict()
# print(orderDict[int("123")][0])


def processOrder(info):
    orderId = getId()
    for ids in orderDict.keys():
        if ids == orderId:
            orderId = getId()

    orderDict[orderId] = info
    return orderId 

daysOfWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
dayOfWeek = datetime.datetime.today().weekday() - 5
# print(daysOfWeek[dayOfWeek])



class ChatBot:
    def __init__(self):
        self.oldDict = {0: ["null", "order", "never"]}
        self.id_ = "0"
        self.name = ""
        self.negativeWords = ["go away", "leave", "nothing", "stop", "exit", "no", "bye", "good bye", "quit", "nope"]
        self.positiveWords = ["yes", "yea", "yeah", "yep", "correct",]
        self.goodbyeMessage = "Sorry to see you go "
        self.posRoutes = {"order": [r'.*purchase.*', r'.*buy.*', r'.*get.*']}
        self.posResponses = ["Your order of {0} should be here by {1}.", "Our {0} sizes typically run large so I would order either your size or bigger.", "We have been selling {0} since 1999."]
        self.clothingBlank = "clothing"
        
    def handleGreet(self):
        prevCustomer = input("Hi there! Do you already have a order ID? \n> ")
        for word in self.positiveWords:
            if word in prevCustomer.lower():
                self.id_ = input("Awesome! What is it? \n> ")
                self.oldDict = pickle.load(open("orders", "rb"))
                self.name = self.oldDict[int(self.id_)][0]
                # print(self.oldDict)
                output = input(f"Ok, what can I do for you {self.oldDict[int(self.id_)][0]}? \n> ")
                if self.continueConvo(output):
                    return print(self.goodbyeMessage + self.name + ".")
                else:
                    return self.convoController(output)
            else:
                self.name = input("Hello there can I please have your name? \n> ")
                output = input(f"Hello there {self.name} how may I help you today? \n> ")
                if self.continueConvo(output):
                    return print(self.goodbyeMessage + self.name + ".")
                else:
                    return self.convoController(output)
    
    def convoController(self, reply):
        for key, value, in self.posRoutes.items():
            for option in value:
                foundMatch = re.match(option, reply.lower())
                if foundMatch and key == "order":
                    return self.handleOrder(reply)
        
        return self.handleReply(reply) 
    
    def handleOrder(self, reply):
        noun = self.determineEntity(reply)
        output = input(f"Am I correct that you wish to purchase a {noun}? \n> ")
        for word in self.positiveWords:
            if word in output.lower():
                orderId = processOrder([self.name, noun, daysOfWeek[dayOfWeek]])
                pickle.dump(orderDict, open("orders", "wb"))
                # print(orderDict)
                print(f"Your order ID is {orderId}. It is important that you remember this as it is how you can access information about you order later.")
                output2 = input(f"Is there anything else I can do for you {self.name}? \n> ")
                if self.continueConvo(output2):
                    return print(self.goodbyeMessage + self.name + ".")
                else:
                    return self.convoController(output2)
            else:
                print("Sorry, lets try that again.")
                output3 = input(f"How can I help you {self.name}? \n> ")
                if self.continueConvo(output3):
                    return print(self.goodbyeMessage + self.name + ".")
                else:
                    return self.convoController(output3)

    def determineIntent(self, reply):
        replyCounted = Counter(preproccess(reply))
        responsesCounted = [Counter(preproccess(response)) for response in self.posResponses]
        simList = [compareOverlap(replyCounted, response) for response in responsesCounted]
        idx = simList.index(max(simList))
        return self.posResponses[idx]
    
    def determineEntity(self, reply):
        nounList = extractNouns(reply)
        noun = computeSimilarity(nounList, self.clothingBlank)
        return noun
    
    def continueConvo(self, reply):
        for word in self.negativeWords:
            if word == reply.lower():
                return True
    
    def handleReply(self, reply):
        intent = self.determineIntent(reply)
        entity = self.determineEntity(reply)
        if intent == self.posResponses[0]:
            print(intent.format(self.oldDict[int(self.id_)][1], self.oldDict[int(self.id_)][2]))
        else:
            print(intent.format(entity))
        output = input("Is there anything else I can help you with? \n> ")
        if self.continueConvo(output):
            return print(self.goodbyeMessage + self.name + ".")
        else:
            return self.convoController(output)

# # print(orderDict)
chatter = ChatBot()
chatter.handleGreet()