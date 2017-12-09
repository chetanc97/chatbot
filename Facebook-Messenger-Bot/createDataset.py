#!/usr/bin/python
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os
import re
from datetime import datetime

personName = input('Enter your full name: ')
fbData = input('Do you have Facebook data to parse through (y/n)?')
googleData = \
    input('Do you have Google Hangouts data to parse through (y/n)?'
              )
linkedInData = \
    input('Do you have LinkedIn data to parse through (y/n)?')


def getGoogleHangoutsData():

    # Putting all the file names in a list

    allFiles = []

    # Edit these file and directory names if you have them saved somewhere else

    for filename in os.listdir('GoogleTextForm'):
        if filename.endswith('.txt'):
            allFiles.append('GoogleTextForm/' + filename)

    responseDictionary = dict()  # The key is the other person's message, and the value is my response

    # Going through each file, and recording everyone's messages to me, and my responses

    for currentFile in allFiles:
        (myMessage, otherPersonsMessage, currentSpeaker) = ('', '', '')
        openedFile = open(currentFile, 'r')
        allLines = openedFile.readlines()
        for (index, lines) in enumerate(allLines):

               # The sender's name is separated by < and >

            leftBracket = lines.find('<')
            rightBracket = lines.find('>')

            # Find messages that I sent

            if lines[leftBracket + 1:rightBracket] == personName:
                if not myMessage:

                       # Want to find the first message that I send (if I send multiple in a row)

                    startMessageIndex = index - 1
                myMessage += lines[rightBracket + 1:]
            elif myMessage:

                   # Now go and see what message the other person sent by looking at previous messages

                for counter in range(startMessageIndex, 0, -1):
                    currentLine = allLines[counter]

                    # In case the message above isn't in the right format

                    if currentLine.find('<') < 0 or currentLine.find('>'
                            ) < 0:
                        (myMessage, otherPersonsMessage,
                         currentSpeaker) = ('', '', '')
                        break
                    if not currentSpeaker:

                           # The first speaker not named me

                        currentSpeaker = \
                            currentLine[currentLine.find('<')
                            + 1:currentLine.find('>')]
                    elif currentSpeaker \
                        != currentLine[currentLine.find('<')
                        + 1:currentLine.find('>')]:

                           # A different person started speaking, so now I know that the first person's message is done

                        otherPersonsMessage = \
                            cleanMessage(otherPersonsMessage)
                        myMessage = cleanMessage(myMessage)
                        responseDictionary[otherPersonsMessage] = \
                            myMessage
                        break
                    otherPersonsMessage = \
                        currentLine[currentLine.find('>') + 1:] \
                        + otherPersonsMessage
                (myMessage, otherPersonsMessage, currentSpeaker) = ('',
                        '', '')
    return responseDictionary


def getFacebookData():
    responseDictionary = dict()
    fbFile = open('D:/chatbot/Facebook-Messenger-Bot/fbMessages.txt', 'r')
    allLines = fbFile.readlines()
    (myMessage, otherPersonsMessage, currentSpeaker) = ('', '', '')
    print('2')
    count = 0
    for (index, lines) in enumerate(allLines):
        rightBracket = lines.find(']') + 2
        justMessage = lines[rightBracket:]
        colon = justMessage.find(':')

        # Find messages that I sent
        print(justMessage)
        print(justMessage[:colon])
        print("Count : ")
        print(count)
        # break
        if count%2 == 0:
            print('4')
            myMessage += justMessage[colon + 2:]
            startMessageIndex = index - 1
            count += 1
        else:
            count += 1
            print('5')

            # Now go and see what message the other person sent by looking at previous messages

            for counter in range(startMessageIndex, 0, -1):
                currentLine = allLines[counter]
                rightBracket = currentLine.find(']') + 2
                justMessage = currentLine[rightBracket:]
                colon = justMessage.find(':')


                    # A different person started speaking, so now I know that the first person's message is done

                otherPersonsMessage = cleanMessage(otherPersonsMessage)
                myMessage = cleanMessage(myMessage)
                responseDictionary[otherPersonsMessage] = myMessage

                otherPersonsMessage = justMessage[colon + 2:] + otherPersonsMessage
            (myMessage, otherPersonsMessage, currentSpeaker) = ('', '',
                    '')
    return responseDictionary


def getLinkedInData():
    df = pd.read_csv('Inbox.csv')
    dateTimeConverter = lambda x: datetime.strptime(x,
            '%B %d, %Y, %I:%M %p')
    responseDictionary = dict()
    peopleContacted = df['From'].unique().tolist()
    for person in peopleContacted:
        receivedMessages = df[df['From'] == person]
        sentMessages = df[df['To'] == person]
        if len(sentMessages) == 0 or len(receivedMessages) == 0:

            # There was no actual conversation

            continue
        combined = pd.concat([sentMessages, receivedMessages])
        combined['Date'] = combined['Date'].apply(dateTimeConverter)
        combined = combined.sort(['Date'])
        (otherPersonsMessage, myMessage) = ('', '')
        firstMessage = True
        for (index, row) in combined.iterrows():
            if row['From'] != personName:
                if myMessage and otherPersonsMessage:
                    otherPersonsMessage = \
                        cleanMessage(otherPersonsMessage)
                    myMessage = cleanMessage(myMessage)
                    responseDictionary[otherPersonsMessage.rstrip()] = \
                        myMessage.rstrip()
                    (otherPersonsMessage, myMessage) = ('', '')
                otherPersonsMessage = otherPersonsMessage \
                    + row['Content'] + ' '
            else:
                if firstMessage:
                    firstMessage = False

                    # Don't include if I am the person initiating the convo

                    continue
                myMessage = myMessage + str(row['Content']) + ' '
    return responseDictionary


def cleanMessage(message):

    # Remove new lines within message

    cleanedMessage = message.replace('\n', ' ').lower()

    # Deal with some weird tokens

    cleanedMessage = cleanedMessage.replace('\xc2\xa0', '')

    # Remove punctuation

    cleanedMessage = re.sub('([.,!?])', '', cleanedMessage)

    # Remove multiple spaces in message

    cleanedMessage = re.sub(' +', ' ', cleanedMessage)
    return cleanedMessage


combinedDictionary = {}
if googleData == 'y':
    print('Getting Google Hangout Data')
    combinedDictionary.update(getGoogleHangoutsData())
if fbData == 'y':
    print('Getting Facebook Data')
    combinedDictionary.update(getFacebookData())
if linkedInData == 'y':
    print('Getting LinkedIn Data')
    combinedDictionary.update(getLinkedInData())
print('Total len of dictionary', len(combinedDictionary))

print('Saving conversation data dictionary')
np.save('conversationDictionary.npy', combinedDictionary)

conversationFile = open('conversationData.txt', 'w')
for (key, value) in combinedDictionary.items():
    if not key.strip() or not value.strip():

        # If there are empty strings

        continue
    conversationFile.write(key.strip() + value.strip())
