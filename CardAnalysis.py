import sys

if sys.version_info[0] < 3:
    execfile("Cards.py")
else:
    exec (open("Cards.py").read())

def generateReadingCardList(txtFilename, numReadingCards):
    output = []

    f = open(txtFilename, "r")
    lines = f.readlines()
    f.close()

    lineNumber = 0
    for line in lines:
        lineNumber += 1
        wordsList = line.split()
        if (len(wordsList) == 2):
            output.append(ReadingCard(wordsList[0], wordsList[1]))
        else:
            raise ValueError("CardAnalysis.py: generateReadingCardList: line " + str(lineNumber) + \
                         " in " + txtFilename + " cannot provide a valid Reading Card.")

    if (lineNumber is not numReadingCards):
        raise ValueError("CardAnalysis.py: generateReadingCardList: number of Reading Cards" \
                         " processed is " + str(lineNumber) + " but not " + str(numReadingCards) + ".")
    return output

def generatePureGrabCardList(readingCardList):
    return [PureGrabbingCard(readingCardList[i].getLastWord()) for i in range(len(readingCardList))]

def generateGrabbingCardList(readingCardList):
    return [GrabbingCard(readingCardList[i].getLastWord()) for i in range(len(readingCardList))]

READING_CARDS = generateReadingCardList("ReadingCards.txt", 100)
PURE_GRABBING_CARDS = generatePureGrabCardList(READING_CARDS)
GRABBING_CARDS = generateGrabbingCardList(READING_CARDS)

def sortFirstWords(readingCardList):
    firstWordList = []
    for i in range(len(readingCardList)):
        firstWordList.append(readingCardList[i].firstWord)
    return sorted(firstWordList)

#remark: for each i, lastWord of readingCardList at i is the same as that of grabbingCardList at i
def assignIndices(readingCardList, grabbingCardList):
    for i in range(len(readingCardList)):
        readingCardList[i].setIndex(i + 1)
        grabbingCardList[i].setIndex(i + 1)

#return firstWord-to-grabbingCard Map
#remark: for each i, lastWord of readingCardList at i is the same as that of grabbingCardList at i
def assignGrabbingCards(readingCardList, grabbingCardList):
    firstWordToGrabbingCardMap = {}
    for i in range(len(readingCardList)):
        firstWordToGrabbingCardMap[readingCardList[i].getFirstWord()] = grabbingCardList[i]
    return firstWordToGrabbingCardMap

def searchReadingCard(readingCardList, sortedFirstWord):
    for i in range(len(readingCardList)):
        if (readingCardList[i].getFirstWord() == sortedFirstWord):
            return readingCardList[i]

def assignDecisionWords(readingCardList, indexToGrabbingCardMap):
    sortedFirstWords = sortFirstWords(readingCardList)
    decisionWords = [[] for i in range(len(readingCardList))]
    index = 0  # Word Index. Move back and forth according to checking letters
    decisionIndex = 0  # Word Index. Increment when the decisionWord is obtained
    letterIndex = 0  # Letter of the given word
    decided = False
    while (decisionIndex < len(readingCardList)):
        letterIndex = len(decisionWords[decisionIndex])
        while ((not decided) and (letterIndex < len(sortedFirstWords[decisionIndex]))):
            letter = sortedFirstWords[decisionIndex][letterIndex]
            index = decisionIndex
            while ((index < len(readingCardList)) and (letterIndex < len(sortedFirstWords[index]))):
                if ((sortedFirstWords[index][letterIndex] is not letter)
                        or (len(decisionWords[decisionIndex]) != len(decisionWords[index]))):
                    break
                index += 1
            if (index == decisionIndex + 1):
                decided = True
            for j in range(decisionIndex, index):
                decisionWords[j].append(letter)
            letterIndex += 1

        decided = False
        decisionIndex += 1

    for l in range(len(decisionWords)):
        decisionWords[l] = "".join(decisionWords[l])

    for k in range(len(sortedFirstWords)):
        indexToGrabbingCardMap[sortedFirstWords[k]].setDecisionWord(decisionWords[k])
        readingCard = searchReadingCard(readingCardList, sortedFirstWords[k])
        readingCard.setDecisionWord(decisionWords[k])

def createDecWordLenList(grabbingCardList):
    decisionWordLengthDic = {}
    for i in range(len(grabbingCardList)):
        if len(grabbingCardList[i].decisionWord) in decisionWordLengthDic:
            decisionWordLengthDic[len(
                grabbingCardList[i].decisionWord)] = decisionWordLengthDic[len(grabbingCardList[i].decisionWord)] + 1
        else:
            decisionWordLengthDic[len(grabbingCardList[i].decisionWord)] = 1
    return decisionWordLengthDic

def analyzeCards(readingCardList, grabbingCardList):
    firstWordList = sortFirstWords(readingCardList)

    firstWordToGrabbingCardMap = assignGrabbingCards(readingCardList, grabbingCardList)
    assignDecisionWords(readingCardList, firstWordToGrabbingCardMap)
    decisionWordLengthList = createDecWordLenList(grabbingCardList)
    """
    for i in range(len(firstWordList)):
        if (len(firstWordToGrabbingCardMap[firstWordList[i]].decisionWord) >=
                1):
            print(firstWordList[i] + " " +
                  firstWordToGrabbingCardMap[firstWordList[i]].decisionWord)

    for i in decisionWordLengthList:
        print(str(i) + " " + str(decisionWordLengthList[i]))
    """

analyzeCards(READING_CARDS, GRABBING_CARDS)
