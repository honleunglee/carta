import pygame  # for grabbing card rect for rendering

class ReadingCard:
    def __init__(self, firstWord, lastWord):
        self.firstWord = firstWord
        self.lastWord = lastWord
        self.index = -1
        self.fullWord = firstWord + " " + lastWord

    def setIndex(self, i):
        self.index = i

    def getFirstWord(self):
        return self.firstWord

    def getLastWord(self):
        return self.lastWord

    def getFullWord(self):
        return self.fullWord

    def getIndex(self):
        return self.index

class PureGrabbingCard:
    def __init__(self, lastWord):
        self.lastWord = lastWord
        self.decisionWord = None
        self.index = -1

    def setDecisionWord(self, word):
        self.decisionWord = word

    def setIndex(self, i):
        self.index = i

    def getLastWord(self):
        return self.lastWord

    def sameLastWord(self, grabbingCard):
        return (self.lastWord == grabbingCard.getLastWord())

# Card in your field, opponent's field, or none of the above
class GrabCardStatus:
    INVALID = 0  # none of the below
    YOU = 1  # in your field
    OPPONENT = 2  # in opponent's field

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class GrabbingCard(PureGrabbingCard):
    def __init__(self, lastWord):
        PureGrabbingCard.__init__(self, lastWord)
        self.rect = None  # the pygame rectangle for rendering
        self.color = None
        self.status = GrabCardStatus.INVALID
        self.frameIndex = -1

    def setRect(self, rect):
        self.rect = rect

    def setColor(self, color):
        self.color = color

    def setStatus(self, status):
        self.status = status

    def setFrameIndex(self, index):
        self.frameIndex = index

    def setRectX(self, x):
        self.rect.x = x

    def setRectY(self, y):
        self.rect.y = y

    def getRect(self):
        return self.rect

    def getColor(self):
        return self.color

    def getStatus(self):
        return self.status

    def getRectX(self):
        return self.rect.x

    def getRectY(self):
        return self.rect.y

    def getPos(self):
        return Point(self.rect.x, self.rect.y)

READING_CARDS = [
    ReadingCard("Starbucks", "Coffee"),
    ReadingCard("Justin", "Bieber"),
    ReadingCard("Abraham", "Lincoln"),
    ReadingCard("George", "Washington"),
    ReadingCard("Space", "Ship"),
    ReadingCard("Mount", "Rainier"),
    ReadingCard("Middle", "School"),
    ReadingCard("Great", "Wall"),
    ReadingCard("Japan", "Tsunami"),
    ReadingCard("Queen", "Elizabeth"),
    ReadingCard("Ski", "Resort"),
    ReadingCard("Highlight", "Pen"),
    ReadingCard("Color", "Pencil"),
    ReadingCard("Index", "Card"),
    ReadingCard("Opium", "War"),
    ReadingCard("Charlie", "Chaplin"),
    ReadingCard("Childhood", "Memory"),
    ReadingCard("Dentist", "Appointment"),
    ReadingCard("Chocolate", "Bar"),
    ReadingCard("World", "Cup"),
    ReadingCard("Yellow", "Fever"),
    ReadingCard("Local", "News"),
    ReadingCard("Iron", "Man"),
    ReadingCard("King", "Arthur"),
    ReadingCard("Potato", "Chips"),
    ReadingCard("Mont", "Blanc"),
    ReadingCard("Himeji", "Castle"),
    ReadingCard("Pythagorean", "Theorem"),
    ReadingCard("Turkey", "Dinner"),
    ReadingCard("Computer", "Science"),
    ReadingCard("Big", "Bang"),
    ReadingCard("Black", "Panther"),
    ReadingCard("Internet", "Explorer"),
    ReadingCard("Google", "Search"),
    ReadingCard("Election", "Day"),
    ReadingCard("Captain", "America"),
    ReadingCard("California", "University"),
    ReadingCard("Merry", "Christmas"),
    ReadingCard("Happy", "Easter"),
    ReadingCard("Social", "Security"),
    ReadingCard("Musical", "Instruments"),
    ReadingCard("Native", "American"),
    ReadingCard("Bill", "Gates"),
    ReadingCard("Play", "Store"),
    ReadingCard("Apple", "Pay"),
    ReadingCard("Microwave", "Oven"),
    ReadingCard("Steve", "Jobs"),
    ReadingCard("Microsoft", "Word"),
    ReadingCard("Samsung", "Galaxy"),
    ReadingCard("Amazon", "Prime"),
    ReadingCard("Honda", "Civic"),
    ReadingCard("Toyota", "Camry"),
    ReadingCard("Bellevue", "College"),
    ReadingCard("Fast", "Food"),
    ReadingCard("Fantastic", "Five"),
    ReadingCard("Shawn", "Mendes"),
    ReadingCard("Tiger", "Shark"),
    ReadingCard("Hong", "Kong"),
    ReadingCard("United", "States"),
    ReadingCard("Donald", "Trump"),
    ReadingCard("Homer", "Simpson"),
    ReadingCard("Table", "Tennis"),
    ReadingCard("Angry", "Bird"),
    ReadingCard("Nintendo", "Switch"),
    ReadingCard("William", "Shakespeare"),
    ReadingCard("Harry", "Potter"),
    ReadingCard("Weight", "Training"),
    ReadingCard("Logan", "Paul"),
    ReadingCard("Dragon", "Ball"),
    ReadingCard("Milk", "Tea"),
    ReadingCard("Video", "Game"),
    ReadingCard("Zigzag", "Path"),
    ReadingCard("Jurassic", "Park"),
    ReadingCard("Barack", "Obama"),
    ReadingCard("Thunder", "Storm"),
    ReadingCard("Capital", "Punishment"),
    ReadingCard("Post", "Office"),
    ReadingCard("South", "Korea"),
    ReadingCard("Fire", "Truck"),
    ReadingCard("Police", "Station"),
    ReadingCard("State", "Court"),
    ReadingCard("Electric", "Car"),
    ReadingCard("Compound", "Interest"),
    ReadingCard("Graphing", "Calculator"),
    ReadingCard("Pacific", "Ocean"),
    ReadingCard("Washing", "Machine"),
    ReadingCard("Nike", "Shoes"),
    ReadingCard("Children", "Playground"),
    ReadingCard("Red", "Bean"),
    ReadingCard("Ice", "Cream"),
    ReadingCard("Transit", "Center"),
    ReadingCard("Treasure", "Island"),
    ReadingCard("Bus", "Stop"),
    ReadingCard("Cell", "Phone"),
    ReadingCard("Protein", "Powder"),
    ReadingCard("Caesar", "Salid"),
    ReadingCard("Orange", "Juice"),
    ReadingCard("Disneyland", "Sea"),
    ReadingCard("North", "Pole"),
    ReadingCard("Solar", "System")
]

def generatePureGrabCardList(readingCardList):
    return [PureGrabbingCard(readingCardList[i].getLastWord()) for i in range(len(readingCardList))]

def generateGrabbingCardList(readingCardList):
    return [GrabbingCard(readingCardList[i].getLastWord()) for i in range(len(readingCardList))]

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

def assignDecisionWords(readingCardList, grabbingCardList, indexToGrabbingCardMap):
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
    assignDecisionWords(readingCardList, grabbingCardList, firstWordToGrabbingCardMap)
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
