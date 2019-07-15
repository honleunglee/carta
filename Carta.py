import pygame
import sys

if sys.version_info[0] < 3:
    execfile("Cards.py")
    execfile("CardStack.py")
else:
    exec (open("Cards.py").read())
    exec (open("CardStack.py").read())

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Color palette; members in Red-Green-Blue (RGB) values
# (x, x, x), each x is 0-255, 255 = 2^8-1
class Colors:
    def __init__(self):
        self.white = (255, 255, 255)
        self.lightGreen = (193, 223, 192)
        self.black = (0, 0, 0)
        self.red = (255, 0, 0)
        self.blue = (0, 0, 255)
        self.yellow = (255, 255, 0)
        self.lightBlue = (4, 234, 250)
        self.green = (0, 255, 0)

class GUIParameters:  # const parameters
    def __init__(self):
        self.screenWidth = 1000
        self.screenHeight = 563  # 16:9 ratio
        self.FPS = 30  # upper bound per frames per second
        self.cardWidth = 52
        self.cardHeight = 73
        self.wordBoxWidth = 270  # Width for wordBox from reading card
        self.wordBoxHeight = 200  # Height for wordBox from reading card
        self.numFrames = 72  # card frames (number of frames per row * self.numCardRows)
        self.frameThickness = 3
        self.horizontalSpacing = 1  # between two frames
        self.verticalSpacing = 10  # between two rows of frames
        self.extraVerticalSpacing = self.verticalSpacing * 2
        self.fontSize = 18
        self.wordFontSize = 36  # for reading card word font size
        self.buttonFontSize = 24
        self.numCardRows = 6
        self.leftMargin = 20  # for grabbing cards in the screen
        self.topMargin = 20  # for grabbing cards in the screen
        self.wordLeftMargin = 10  # Reading card word in the wordBox
        self.wordTopMargin = 85  # Reading card word in the wordBox
        self.infoScreenStartX = self.screenWidth * 7 // 10
        self.wordBoxStart = Point(720, 100)  # left top for wordBox from reading word
        self.stackStart = Point(750, 400)  # left top point for stack of grabbing cards
        self.leftCardMargin = 5  # for last word in a grabbing card
        self.topCardMargin = 5  # for last word in a grabbing card
        self.doneButtonStart = Point(816, 300)  # left top for "Done" button box
        self.buttonBoxWidth = 70  # Width for "Done" button box
        self.buttonBoxHeight = 40  # Height for "Done" button box
        self.leftDoneMargin = 10  # for "Done" button in the button box
        self.topDoneMargin = 10  # for "Done" button in the button box
        self.leftTimeMargin = 5  # for time in info screen
        self.topTimeMargin = 5  # for time in info screen
        self.displayLatency = 500  # display one character in reading card every self.displayLatency ms

# Carta Game Phase enum (in python 3, import enum as Enum)
# Phase order 1-2-3-4-5-1-2-3-4-5...... until one player has no cards --> 6
class Phase:
    INVALID = 0  # none of the states below
    OPPONENT_SET_UP = 1  # opoonent setting his/her cards in his/her field
    YOUR_SET_UP = 2  # you setting your cards in your field
    GRABBING = 3  # grabbing: compete between you and opponent
    OPPONENT_ADJUSTMENT = 4  # opponent may give a card to you
    YOUR_ADJUSTMENT = 5  # you may give a card to opponent
    END_GAME = 6

class GrabPhaseInfo:
    def __init__(self):
        self.savedStartTime = False
        self.startTime = 0  # time of the grabbing phase's start
        self.yourGrabCardLastWord = ""
        self.yourTime = None  # time of pressing the grabbing card
        self.oppoGrabCardLastWord = ""
        self.opponentTime = None  # time of opponent pressing the grabbing card
        self.oppoGrabbedCard = False
        self.timesUp = False
        self.roundEnded = False
        self.youGrabbedCard = False
        self.youWin = False
        self.opponentWin = False

class CartaParameters:  # constant parameters
    def __init__(self):
        self.opponentTimeForStupidAI = 10000  # ms
        self.maxStartGrabbingTime = 18000  # ms
        self.maxEndGrabbingTime = 19000
        self.opponentSuccessProb = 0.8

class Carta:
    def __init__(self):
        self.initGame()
        self.initRendering()
        self.initReadingCards()
        self.initCardFrames()
        self.initGrabbingCards()

        self.clock = pygame.time.Clock()
        self.running = True  # track if the game is running

    def initGame(self):
        pygame.init()
        self.GPinfo = GrabPhaseInfo()
        self.parameters = CartaParameters()
        self.phase = Phase.OPPONENT_SET_UP
        self.debugMode = False  # default is False

        self.usedGrabbingCards = CardStack([])  # grabbed grabbing card
        self.usedReadingCards = CardStack([])  # read reading card

        self.numYourGrabCardInPlay = len(GRABBING_CARDS) // 4
        self.numOppoGrabCardInPlay = len(GRABBING_CARDS) // 4
        self.displayReadCardStartTime = 0

        self.yourGrabCardAssigned = False

    def initRendering(self):
        self.colors = Colors()
        self.GUIParameters = GUIParameters()
        self.screen = pygame.display.set_mode((self.GUIParameters.screenWidth, self.GUIParameters.screenHeight))
        pygame.display.set_caption("Carta")

        pygame.font.init()
        # for grabbing card word
        self.font = pygame.font.SysFont('freesans', self.GUIParameters.fontSize)
        # for reading card word
        self.wordFont = pygame.font.SysFont('freesans', self.GUIParameters.wordFontSize)
        # for "Done" button word
        self.doneFont = pygame.font.SysFont('freesand', self.GUIParameters.buttonFontSize)

        self.infoScreen = pygame.rect.Rect(self.GUIParameters.infoScreenStartX, 0,
                                           self.GUIParameters.screenWidth - self.GUIParameters.infoScreenStartX,
                                           self.GUIParameters.screenHeight)

        self.doneButton = pygame.rect.Rect(self.GUIParameters.doneButtonStart.x, self.GUIParameters.doneButtonStart.y,
                                           self.GUIParameters.buttonBoxWidth, self.GUIParameters.buttonBoxHeight)

        self.displayReadingCard = False  # True if to display reading card

    def initReadingCards(self):
        # Shuffle and put 50 cards into the readingCardStack
        self.readingCardStack = CardStack(READING_CARDS)
        self.readingCardStack.shuffle()
        self.readingCardBox = pygame.rect.Rect(self.GUIParameters.wordBoxStart.x, self.GUIParameters.wordBoxStart.y,
                                               self.GUIParameters.wordBoxWidth, self.GUIParameters.wordBoxHeight)

        # About the current reading card in play
        self.curReadingCard = None
        self.numReadCardChars = 0  # display reading card word up to this number

    def createCardFrame(self, lt):
        rb = Point(lt.x + self.GUIParameters.cardWidth, lt.y + self.GUIParameters.cardHeight)
        return [(lt.x, lt.y), (lt.x, rb.y), (rb.x, rb.y), (rb.x, lt.y)]

    def setFramesInARow(self, stepX, start, frames):  # start and frames will be modified
        for k in range(self.GUIParameters.numFrames // self.GUIParameters.numCardRows):
            cardFrameLeftTop = Point(start.x + k * stepX, start.y)
            frames.append(self.createCardFrame(cardFrameLeftTop))
        start.y += self.GUIParameters.cardHeight + \
                   self.GUIParameters.verticalSpacing

    def initCardFrames(self):
        self.frames = []  # card frames
        start = Point(self.GUIParameters.leftMargin, self.GUIParameters.topMargin)
        stepX = self.GUIParameters.cardWidth + self.GUIParameters.horizontalSpacing
        for i in range(self.GUIParameters.numCardRows // 2):
            self.setFramesInARow(stepX, start, self.frames)

        start.y += self.GUIParameters.extraVerticalSpacing  # separation between yours and opponent

        for i in range(self.GUIParameters.numCardRows // 2, self.GUIParameters.numCardRows):
            self.setFramesInARow(stepX, start, self.frames)

        # only consider your frames
        self.occupied = [False for i in range(len(self.frames) // 2)]
        self.cardToFrameMap = {}  # both your and opponent cards and frames
        self.numYourFramesOccupied = 0

    def initGrabbingCards(self):
        grabbingCardStack = CardStack(GRABBING_CARDS)
        grabbingCardStack.shuffle()
        halfStack = grabbingCardStack.draw(len(GRABBING_CARDS) // 2)
        self.yourGrabbingCards = [halfStack[i] for i in range(0, len(halfStack), 2)]
        self.opponentGrabbingCards = [halfStack[i] for i in range(1, len(halfStack), 2)]
        self.grabbingCardsInPlay = self.yourGrabbingCards + self.opponentGrabbingCards

        # First handle your grabbing cards, then opponents
        self.lastWords = [card.getLastWord() for card in self.yourGrabbingCards]
        self.lastWords += [card.getLastWord() for card in self.opponentGrabbingCards]

        # grabbing cards as rectangles in screen
        # First half is yours, second half is opponent's
        self.cards = [None] * len(self.lastWords)
        self.cardColors = [self.colors.white] * len(self.lastWords)

        # Your cards start at the card stack on the right of screen
        for i in range(len(self.cards) // 2):
            self.cards[i] = pygame.rect.Rect(self.GUIParameters.stackStart.x, self.GUIParameters.stackStart.y,
                                             self.GUIParameters.cardWidth, self.GUIParameters.cardHeight)

        if (self.phase == Phase.OPPONENT_SET_UP):
            # Opponent cards start at their designated positions
            # For now, assume they are randomly placed
            frameIndexList = [k for k in range(0, len(self.frames) // 2)]
            # sample (len(self.cards) // 2) indices from (len(self.frames) // 2) frames
            random.seed(time.time())
            sampledFrames = random.sample(frameIndexList, self.numOppoGrabCardInPlay)

            for i in range(len(self.cards) // 2, len(self.cards)):
                frameIndex = sampledFrames[i - (len(self.cards) // 2)]
                self.cards[i] = pygame.rect.Rect(self.frames[frameIndex][0][0], self.frames[frameIndex][0][1],
                                                 self.GUIParameters.cardWidth, self.GUIParameters.cardHeight)
            self.phase = Phase.YOUR_SET_UP

        self.cardDragging = False
        self.touchYourCard = False

    # 0 ms --> pygame.init(). Get current time relative to pygame.init().
    def getTime_ms(self):
        return pygame.time.get_ticks()

    # return integer time
    def getIntTime_s(self):
        return int(round(self.getTime_ms() / 1000))

    # pos is the position of left top corner of a card
    def findNearestFrame(self, pos):
        minDistanceSq = sys.float_info.max
        bestFrameIndex = self.GUIParameters.numFrames
        # for loop over your frames (not all frames)
        for i in range(self.GUIParameters.numFrames // 2, self.GUIParameters.numFrames):
            if not self.occupied[i - (self.GUIParameters.numFrames // 2)]:
                distSq = (self.frames[i][0][0] - pos.x)**2 + \
                         (self.frames[i][0][1] - pos.y)**2
                if (distSq < minDistanceSq):
                    minDistanceSq = distSq
                    bestFrameIndex = i
        return bestFrameIndex

    def fillScreens(self):
        self.screen.fill(self.colors.lightGreen)
        pygame.draw.rect(self.screen, self.colors.lightBlue, self.infoScreen)

    def renderTime(self):
        timeString = str(self.getIntTime_s())  # in seconds
        timeSurface = self.wordFont.render(timeString, False, self.colors.black)
        self.screen.blit(timeSurface, (self.infoScreen.x + self.GUIParameters.leftTimeMargin,
                                       self.infoScreen.y + self.GUIParameters.topTimeMargin))

    def renderCardFrames(self):
        for j in range(len(self.frames) // 2):
            pygame.draw.lines(self.screen, self.colors.red, True, self.frames[j], self.GUIParameters.frameThickness)
        for j in range(len(self.frames) // 2, len(self.frames)):
            pygame.draw.lines(self.screen, self.colors.blue, True, self.frames[j], self.GUIParameters.frameThickness)

    def renderSingleCardAndWord(self, cardIndex):
        # self.cards and self.lastWords share the same indexing
        pygame.draw.rect(self.screen, self.cardColors[cardIndex], self.cards[cardIndex])
        textsurface = self.font.render(self.lastWords[cardIndex], False, self.colors.black)

        if (cardIndex >= len(self.cards) // 2):  # card is on opponent field
            textsurface = pygame.transform.rotate(textsurface, 180)

        self.screen.blit(textsurface, (self.cards[cardIndex].x + self.GUIParameters.leftCardMargin,
                                       self.cards[cardIndex].y + self.GUIParameters.topCardMargin))

    def renderGrabbingCardsAndWords(self, dragIndex):
        # Render cards and write last words on the cards
        # First render the non-dragging cards
        for i in range(len(self.cards) - 1, -1, -1):
            if (i is not dragIndex):
                self.renderSingleCardAndWord(i)

        # Render the dragging card, to make sure it is always
        # rendered on top
        self.renderSingleCardAndWord(dragIndex)

    def renderReadingCardWords(self):
        # Render first and last words on empty space on the right of screen
        pygame.draw.rect(self.screen, self.colors.black, self.readingCardBox)
        if (self.curReadingCard is None):
            return

        displayOneMoreChar = (self.displayReadCardStartTime +
                              (self.numReadCardChars + 1) * self.GUIParameters.displayLatency < self.getTime_ms())

        if (self.numReadCardChars < len(self.curReadingCard.getFullWord()) and \
            displayOneMoreChar):
            self.numReadCardChars += 1

        textsurface = self.wordFont.render(self.curReadingCard.getFullWord()[:self.numReadCardChars], False,
                                           self.colors.white)

        self.screen.blit(textsurface, (self.readingCardBox.x + self.GUIParameters.wordLeftMargin,
                                       self.readingCardBox.y + self.GUIParameters.wordTopMargin))

    def renderDoneButton(self):
        pygame.draw.rect(self.screen, self.colors.green, self.doneButton)
        textsurface = self.doneFont.render("Done", False, self.colors.black)
        self.screen.blit(textsurface, (self.doneButton.x + self.GUIParameters.leftDoneMargin,
                                       self.doneButton.y + self.GUIParameters.topDoneMargin))

    # Check if the time between start time and current time is 18 sec
    def checkTime(self):
        if ((self.getTime_ms() - self.GPinfo.startTime >= self.parameters.maxStartGrabbingTime) and \
            (self.getTime_ms() - self.GPinfo.startTime <= self.parameters.maxEndGrabbingTime)):
            self.GPinfo.timesUp = True

    # Save the starting time of the round
    def saveStartTime_ms(self):
        self.GPinfo.startTime = self.getTime_ms()
        self.GPinfo.savedStartTime = True

    # Save the time where player select the grabbing card
    def saveYourTime_ms(self):
        self.GPinfo.yourTime = self.getTime_ms()

    # Save the grabbing card that was selected
    def saveYourGrabbingCard(self, grabbingIndex):
        if (self.GPinfo.youGrabbedCard is False):
            self.GPinfo.yourGrabCardLastWord = self.lastWords[grabbingIndex[0]]
            self.GPinfo.youGrabbedCard = True

    def checkGrabbingAvailable(self):
        for i in range(len(self.grabbingCardsInPlay)):
            if (self.grabbingCardsInPlay[i].getLastWord() == self.curReadingCard.getLastWord()):
                return True
        return False

    # Stupid AI: validated
    def opponentGrabsCard(self):
        takeCorrectCard = False
        random.seed(time.time())
        x = random.uniform(0, 1)
        if (x <= self.parameters.opponentSuccessProb):
            takeCorrectCard = True
        for i in range(len(self.grabbingCardsInPlay)):
            if ((self.grabbingCardsInPlay[i].getLastWord() == self.curReadingCard.getLastWord()) and \
                (takeCorrectCard)):
                self.GPinfo.oppoGrabCardLastWord = self.grabbingCardsInPlay[i].getLastWord()
                break
            elif ((self.grabbingCardsInPlay[i].getLastWord() != self.curReadingCard.getLastWord()) and \
                  (not takeCorrectCard)):
                self.GPinfo.oppoGrabCardLastWord = self.grabbingCardsInPlay[i].getLastWord()
                break

        self.GPinfo.opponentTime = self.GPinfo.startTime + self.parameters.opponentTimeForStupidAI
        self.GPinfo.oppoGrabbedCard = True

        if (self.debugMode):
            if ((takeCorrectCard) and (self.GPinfo.oppoGrabCardLastWord != "")):
                print("Carta.py: opponentGrabsCard: opponent take correct card")
            elif (not takeCorrectCard):
                print("Carta.py: opponentGrabsCard: opponent take wrong card")
            else:
                print("Carta.py: opponentGrabsCard: opponent wants the correct card, but it is not available")

    def decideWinner(self):
        statement = ""
        # Both player grabbed the right card, but you grabbed it faster than opponent
        if ((self.GPinfo.yourGrabCardLastWord == self.curReadingCard.getLastWord()) and \
            (self.GPinfo.oppoGrabCardLastWord == self.curReadingCard.getLastWord()) and \
            (self.GPinfo.yourTime < self.GPinfo.opponentTime)):
            self.GPinfo.youWin = True
            self.GPinfo.opponentWin = False
            statement = "Both player grabbed the right card, but you grabbed it faster than opponent"
        # Both player grabbed the right card, but opponent grabbed it faster than you
        elif ((self.GPinfo.yourGrabCardLastWord == self.curReadingCard.getLastWord()) and \
              (self.GPinfo.oppoGrabCardLastWord == self.curReadingCard.getLastWord()) and \
              (self.GPinfo.yourTime > self.GPinfo.opponentTime)):
            self.GPinfo.youWin = False
            self.GPinfo.opponentWin = True
            statement = "Both player grabbed the right card, but opponent grabbed it faster than you"
        # you didn't grab the right card, but opponent grabbed the right card
        elif ((self.GPinfo.yourGrabCardLastWord != self.curReadingCard.getLastWord()) and \
              (self.GPinfo.oppoGrabCardLastWord == self.curReadingCard.getLastWord())):
            self.GPinfo.youWin = False
            statement = "you didn't grab the right card, but opponent grabbed the right card"
        # you grabbed the right card, but opponent didn't grab the right card
        elif ((self.GPinfo.yourGrabCardLastWord == self.curReadingCard.getLastWord()) and \
              (self.GPinfo.oppoGrabCardLastWord != self.curReadingCard.getLastWord())):
            self.GPinfo.youWin = True
            self.GPinfo.opponentWin = False
            statement = "you grabbed the right card, but opponent didn't grab the right card"
        # if the time pass 18 seconds after start time and it checks that there is no grabbing card match the last word of the currentReadingcard,
        # and both player didn't grabbed any grabbing card, then both player wins
        elif ((self.GPinfo.timesUp is True) and \
              (self.checkGrabbingAvailable() is False) and \
              (self.GPinfo.yourGrabCardLastWord == "") and \
              (self.GPinfo.oppoGrabCardLastWord == "")):
            self.GPinfo.youWin = True
            self.GPinfo.opponentWin = True
            statement = "No available GrabCard, both players win"
        # if the time pass start time is 18 seconds and it checks that there is no grabbing card match the last word of the currentReadingcard,
        # and opponent didn't grabbed any grabbing card, but you garbbed a card, then opponent wins
        elif ((self.GPinfo.timesUp is True) and \
              (self.checkGrabbingAvailable() is False) and \
              (self.GPinfo.yourGrabCardLastWord != "") and \
              (self.GPinfo.oppoGrabCardLastWord == "")):
            self.GPinfo.youWin = False
            self.GPinfo.opponentWin = True
            statement = "No available GrabCard, opponent win"
        # if the time pass start time is 18 seconds and it checks that there is no grabbing card match the last word of the currentReadingcard,
        # and opponentgrabbed a grabbing card, but you didn't grabbed any card, then you wins
        elif ((self.GPinfo.timesUp is True) and \
              (self.checkGrabbingAvailable() is False) and \
              (self.GPinfo.yourGrabCardLastWord == "") and \
              (self.GPinfo.oppoGrabCardLastWord != "")):
            self.GPinfo.youWin = True
            self.GPinfo.opponentWin = False
            statement = "No available GrabCard, you win"
        else:
            self.GPinfo.youWin = False
            self.GPinfo.opponentWin = False
            statement = "Both players grab wrong card"
        if (self.debugMode):
            print(statement)
        if (self.GPinfo.youWin):
            print("You Win")
        self.GPinfo.roundEnded = True

    # The function updates dragIndex, grabbingIndex, mouse, offset
    def selectCard(self, event, dragIndex, grabbingIndex, mouse, offset):
        for j in range(len(self.cards)):
            # If mouse click is on self.cards[j]
            if self.cards[j].collidepoint(event.pos):
                self.cardDragging = (self.phase == Phase.YOUR_SET_UP)
                self.touchYourCard = (j < self.numYourGrabCardInPlay)
                mouse.x, mouse.y = event.pos
                dragIndex[0] = j
                grabbingIndex[0] = j
                offset.x = self.cards[dragIndex[0]].x - mouse.x
                offset.y = self.cards[dragIndex[0]].y - mouse.y
                self.cardColors[j] = self.colors.yellow
                if j in self.cardToFrameMap:
                    self.occupied[self.cardToFrameMap[j] - (len(self.frames) // 2)] = False
                    self.numYourFramesOccupied -= 1
                break

    def randomAssignYourGrabCards(self):
        frameIndexList = [k for k in range(len(self.frames) // 2, len(self.frames))]

        # self.numYourGrabCardInPlay indices from (len(self.frames) // 2) frames
        random.seed(time.time())
        sampledFrames = random.sample(frameIndexList, self.numYourGrabCardInPlay)

        for i in range(self.numYourGrabCardInPlay):
            frameIndex = sampledFrames[i]
            self.cards[i] = pygame.rect.Rect(self.frames[frameIndex][0][0], self.frames[frameIndex][0][1],
                                             self.GUIParameters.cardWidth, self.GUIParameters.cardHeight)
            self.cardToFrameMap[i] = frameIndex
            self.occupied[self.cardToFrameMap[i] - (len(self.frames) // 2)] = True
            self.numYourFramesOccupied += 1

        self.yourGrabCardAssigned = True

    # The function updates mouse and phase
    def pressDoneButton(self, event, mouse):
        # if the "Done" button was pushed while it is my setup phase, then move onto grabbing phase
        if ((self.doneButton.collidepoint(event.pos)) and \
            (self.phase == Phase.YOUR_SET_UP) and \
            (self.numYourFramesOccupied >= self.numYourGrabCardInPlay)):
            self.phase = Phase.GRABBING
            self.displayReadCardStartTime = self.getTime_ms()

    # Draw a reading card
    def drawReadingCard(self):
        if ((self.phase == Phase.GRABBING) and \
            (self.displayReadingCard is False)):
            self.curReadingCard = self.readingCardStack.drawOneCard()
            self.numReadCardChars = 0
            self.displayReadingCard = True

    # The function updates dragIndex, mouse, offset
    def handleEvent(self, event, dragIndex, grabbingIndex, mouse, offset):
        if event.type == pygame.QUIT:  # Click the X in the window
            self.running = False

        # event.button:
        # 1 = left click
        # 2 = middle click
        # 3 = right click
        # 4 = scroll up
        # 5 = scroll down
        elif ((event.type == pygame.MOUSEBUTTONDOWN) and \
              (event.button == 1)):
            self.selectCard(event, dragIndex, grabbingIndex, mouse, offset)
            if (self.phase is Phase.GRABBING):
                self.saveYourTime_ms()
                self.saveYourGrabbingCard(grabbingIndex)
            if (self.phase == Phase.YOUR_SET_UP):
                self.pressDoneButton(event, mouse)
                self.drawReadingCard()

        # The below only works in your set up phase
        elif ((event.type == pygame.MOUSEBUTTONUP) and \
              (event.button == 1)):
            self.cardColors[dragIndex[0]] = self.colors.white
            if (self.cardDragging and self.touchYourCard):
                frameIndex = self.findNearestFrame(Point(self.cards[dragIndex[0]].x, self.cards[dragIndex[0]].y))
                self.cards[dragIndex[0]].x = self.frames[frameIndex][0][0]
                self.cards[dragIndex[0]].y = self.frames[frameIndex][0][1]
                cardIndex = dragIndex[0]
                frameIndexOffset = frameIndex - (len(self.frames) // 2)
                self.occupied[frameIndexOffset] = True
                self.numYourFramesOccupied += 1
                self.cardToFrameMap[cardIndex] = frameIndex

                self.cardDragging = False
                self.touchYourCard = False

        # Left click and drag your card
        elif ((event.type == pygame.MOUSEMOTION) and \
           self.cardDragging and \
           self.touchYourCard):
            mouse.x, mouse.y = event.pos
            self.cards[dragIndex[0]].x = mouse.x + offset.x
            self.cards[dragIndex[0]].y = mouse.y + offset.y

    def process(self):
        dragIndex = [0]  # index of the card being dragged
        grabbingIndex = [0]  # index of the card being grabbed
        # record mouse position relative to left top corner of the whole screen
        mouse = Point(0, 0)
        # record left top corner of the dragging card relative to mouse position
        offset = Point(0, 0)
        while self.running:
            for event in pygame.event.get():
                self.handleEvent(event, dragIndex, grabbingIndex, mouse, offset)

            self.fillScreens()
            self.renderTime()
            self.renderCardFrames()
            if (self.phase is Phase.YOUR_SET_UP):
                if (self.debugMode and self.yourGrabCardAssigned is False):
                    self.randomAssignYourGrabCards()
                self.renderDoneButton()
            self.renderGrabbingCardsAndWords(dragIndex[0])
            if (self.displayReadingCard):
                if (self.GPinfo.savedStartTime is False):
                    self.saveStartTime_ms()
                self.checkTime()
                self.renderReadingCardWords()
                if (self.GPinfo.oppoGrabbedCard is False):
                    self.opponentGrabsCard()
                if ((self.GPinfo.roundEnded is False) and (self.GPinfo.timesUp is True)):
                    if (self.GPinfo.yourTime is None):
                        self.saveYourTime_ms()
                    self.decideWinner()

            pygame.display.flip()  # update rendering contents
            self.clock.tick(self.GUIParameters.FPS)

    def quit(self):
        pygame.quit()
