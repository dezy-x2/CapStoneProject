# CapStoneProject
Shopping Helper
Dans-a-dev
This is a retrieval based Chatbot. I chose to use retrieval instead of open domain because for the purposes of creating a chatbot to help you purchase and find information on clothing items it seemed like the best idea. 
It could be used at a clothing store or with a little modification any kind of retail store
I mainly used Retrieval based but there is also a bit of rule based to help smooth out the clothes purchasing. 

The main struggle with this was implementing it to actually be usefull. When i first created it it could mainly just tell you what clothing item was coming on a made up day. Another challenge was that I realized that in order for it to be able to remember you it I needed to create an external database so it would't restart everytime. For this problem I sort of cheated by using pickle. It is a module that will store you data for you. It is a simple fix and I may later improve on it. There are not many ethical concerns for this as it does not ask for much information. If it were to really be used however you would need a secure place to store data since you would need to access information like credit card numbers emails and addresses

I did have to use several modules to get this done including:
Regex - this was to sort through words and to clean sentences to make them easier to read
spaCy - this was to vecorize words so that they could be properly compared to each other
nltk.corpus - this was for the stop words to help speed up run time
nltk.tokenize - this was to tokenize the sentences for me
nltk - this was for the part of speech tagging
collections - this was where I got the counter from to do BoW
datetime - this was to get the day of the week that the package would arrive
random - this was to get the order ID for each customer
pickle - this was what stored the data for me
