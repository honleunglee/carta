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
        self.wordBoxStart = Point(
            720, 100)  # left top for wordBox from reading word
        self.stackStart = Point(
            750, 400)  # left top point for stack of grabbing cards
        self.leftCardMargin = 5  # for last word in a grabbing card
        self.topCardMargin = 5  # for last word in a grabbing card
        self.doneButtonStart = Point(816,
                                     300)  # left top for "Done" button box
        self.buttonBoxWidth = 70  # Width for "Done" button box
        self.buttonBoxHeight = 40  # Height for "Done" button box
        self.leftDoneMargin = 10  # for "Done" button in the button box
        self.topDoneMargin = 10  # for "Done" button in the button box
        self.leftTimeMargin = 5  # for time in info screen
        self.topTimeMargin = 5  # for time in info screen

# Carta Game Phase enum (in python 3, import enum as Enum)
# Phase order 1-2-3-4-5-1-2-3-4-5...... until one player has no cards --> 6
class Phase:
    INVALID = 0  # none of the states below
    OPPONENT_SET_UP = 1  # opoonent setting his/her cards in his/her field
    YOUR_SET_UP = 2  # you setting your cards in your field
    DRAWING = 3  # draw a reading card
    GRABBING = 4  # grabbing: compete between you and opponent
    OPPONENT_ADJUSTMENT = 5  # opponent may give a card to you
    YOUR_ADJUSTMENT = 6  # you may give a card to opponent
    END_GAME = 6

class CartaInfo:
    def __init__(self):
        self.startTime = 0  # time of the grabbing phase's start
        self.yourGrabbingCard = None
        self.yourTime = None  # time of pressing the grabbing card
        self.opponentGrabbingCard = None
        self.opponentTime = None  # time of opponent pressing the grabbing card
        self.youWin = False
        self.opponentMoved = False

class CartaParameters:  # constant parameters
    def __init__(self):
        self.opponentTimeForStupidAI = 10000
        self.maxGrabbingTime = 18000
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
        self.info = CartaInfo()
        self.parameters = CartaParameters()
        self.phase = Phase.OPPONENT_SET_UP
        self.usedGrabbingCards = CardStack([])  # grabbed grabbing card
        self.usedReadingCards = CardStack([])  # read reading card

    def initRendering(self):
        self.colors = Colors()
        self.GUIParameters = GUIParameters()
        self.screen = pygame.display.set_mode(
            (self.GUIParameters.screenWidth, self.GUIParameters.screenHeight))
        pygame.display.set_caption("Carta")

        pygame.font.init()
        # for grabbing card word
        self.font = pygame.font.SysFont('freesans',
                                        self.GUIParameters.fontSize)
        # for reading card word
        self.wordFont = pygame.font.SysFont('freesans',
                                            self.GUIParameters.wordFontSize)
        # for "Done" button word
        self.doneFont = pygame.font.SysFont('freesand',
                                            self.GUIParameters.buttonFontSize)

        self.infoScreen = pygame.rect.Rect(
            self.GUIParameters.infoScreenStartX, 0,
            self.GUIParameters.screenWidth -
            self.GUIParameters.infoScreenStartX,
            self.GUIParameters.screenHeight)

        self.doneButton = pygame.rect.Rect(
            self.GUIParameters.doneButtonStart.x,
            self.GUIParameters.doneButtonStart.y,
            self.GUIParameters.buttonBoxWidth,
            self.GUIParameters.buttonBoxHeight)

    def initReadingCards(self):
        # Shuffle and put 50 cards into the readingCardStack
        self.readingCardStack = CardStack(READING_CARDS)
        self.readingCardStack.shuffle()
        self.readingCardBox = pygame.rect.Rect(
            self.GUIParameters.wordBoxStart.x,
            self.GUIParameters.wordBoxStart.y, self.GUIParameters.wordBoxWidth,
            self.GUIParameters.wordBoxHeight)

        self.currentReadingCard = None

    def createCardFrame(self, lt):
        rb = Point(lt.x + self.GUIParameters.cardWidth,
                   lt.y + self.GUIParameters.cardHeight)
        return [(lt.x, lt.y), (lt.x, rb.y), (rb.x, rb.y), (rb.x, lt.y)]

    def setFramesInARow(self, stepX, start,
                        frames):  # start and frames will be modified
        for k in range(self.GUIParameters.numFrames //
                       self.GUIParameters.numCardRows):
            cardFrameLeftTop = Point(start.x + k * stepX, start.y)
            frames.append(self.createCardFrame(cardFrameLeftTop))
        start.y += self.GUIParameters.cardHeight + \
                   self.GUIParameters.verticalSpacing

    def initCardFrames(self):
        self.frames = []  # card frames
        start = Point(self.GUIParameters.leftMargin,
                      self.GUIParameters.topMargin)
        stepX = self.GUIParameters.cardWidth + self.GUIParameters.horizontalSpacing
        for i in range(self.GUIParameters.numCardRows // 2):
            self.setFramesInARow(stepX, start, self.frames)

        start.y += self.GUIParameters.extraVerticalSpacing  # separation between yours and opponent

        for i in range(self.GUIParameters.numCardRows // 2,
                       self.GUIParameters.numCardRows):
            self.setFramesInARow(stepX, start, self.frames)

        # only consider your frames
        self.occupied = [False for i in range(len(self.frames) // 2)]
        self.cardToFrameMap = {}  # both your and opponent cards and frames
        self.numYourFramesOccupied = 0

    def initGrabbingCards(self):
        grabbingCardStack = CardStack(GRABBING_CARDS)
        grabbingCardStack.shuffle()
        halfStack = grabbingCardStack.draw(len(GRABBING_CARDS) // 2)
        self.yourGrabbingCards = [
            halfStack[i] for i in range(0, len(halfStack), 2)
        ]
        self.opponentGrabbingCards = [
            halfStack[i] for i in range(1, len(halfStack), 2)
        ]
        self.grabbingCardsInPlay = self.yourGrabbingCards + self.opponentGrabbingCards

        # First handle your grabbing cards, then opponents
        self.lastWords = [
            card.getLastWord() for card in self.yourGrabbingCards
        ]
        self.lastWords += [
            card.getLastWord() for card in self.opponentGrabbingCards
        ]

        # grabbing cards as rectangles in screen
        # First half is yours, second half is opponent's
        self.cards = [None] * len(self.lastWords)
        self.cardColors = [self.colors.white] * len(self.lastWords)

        # Your cards start at the card stack on the right of screen
        for i in range(len(self.cards) // 2):
            self.cards[i] = pygame.rect.Rect(self.GUIParameters.stackStart.x,
                                             self.GUIParameters.stackStart.y,
                                             self.GUIParameters.cardWidth,
                                             self.GUIParameters.cardHeight)

        if (self.phase == Phase.OPPONENT_SET_UP):
            # Opponent cards start at their designated positions
            # For now, assume they are randomly placed
            frameIndexList = [k for k in range(0, len(self.frames) // 2)]
            # sample (len(self.cards) // 2) indices from (len(self.frames) // 2) frames
            random.seed(time.time())
            sampledFrames = random.sample(frameIndexList, len(self.cards) // 2)

            for i in range(len(self.cards) // 2, len(self.cards)):
                frameIndex = sampledFrames[i - (len(self.cards) // 2)]
                self.cards[i] = pygame.rect.Rect(self.frames[frameIndex][0][0],
                                                 self.frames[frameIndex][0][1],
                                                 self.GUIParameters.cardWidth,
                                                 self.GUIParameters.cardHeight)
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
        for i in range(self.GUIParameters.numFrames // 2,
                       self.GUIParameters.numFrames):
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
        timeSurface = self.wordFont.render(timeString, False,
                                           self.colors.black)
        self.screen.blit(
            timeSurface,
            (self.infoScreen.x + self.GUIParameters.leftTimeMargin,
             self.infoScreen.y + self.GUIParameters.topTimeMargin))

    def renderCardFrames(self):
        for j in range(len(self.frames) // 2):
            pygame.draw.lines(self.screen, self.colors.red, True,
                              self.frames[j],
                              self.GUIParameters.frameThickness)
        for j in range(len(self.frames) // 2, len(self.frames)):
            pygame.draw.lines(self.screen, self.colors.blue, True,
                              self.frames[j],
                              self.GUIParameters.frameThickness)

    def renderSingleCardAndWord(self, cardIndex):
        # self.cards and self.lastWords share the same indexing
        pygame.draw.rect(self.screen, self.cardColors[cardIndex],
                         self.cards[cardIndex])
        textsurface = self.font.render(self.lastWords[cardIndex], False,
                                       self.colors.black)

        if (cardIndex >= len(self.cards) // 2):  # card is on opponent field
            textsurface = pygame.transform.rotate(textsurface, 180)

        self.screen.blit(
            textsurface,
            (self.cards[cardIndex].x + self.GUIParameters.leftCardMargin,
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
        # TODO: Why if (phase == GRABBING) does not work here?
        if ((self.phase == Phase.DRAWING) or (self.phase == Phase.GRABBING)):
            if (self.currentReadingCard is not None):
                textsurface = self.wordFont.render(
                    (self.currentReadingCard.getFirstWord() + " " +
                     self.currentReadingCard.getLastWord()), False,
                    self.colors.white)

                self.screen.blit(
                    textsurface,
                    (self.readingCardBox.x + self.GUIParameters.wordLeftMargin,
                     self.readingCardBox.y + self.GUIParameters.wordTopMargin))

    def renderDoneButton(self):
        pygame.draw.rect(self.screen, self.colors.red, self.doneButton)
        textsurface = self.doneFont.render("Done", False, self.colors.black)
        self.screen.blit(
            textsurface,
            (self.doneButton.x + self.GUIParameters.leftDoneMargin,
             self.doneButton.y + self.GUIParameters.topDoneMargin))

    # Save the starting time of the round
    def saveStartTime_ms(self):
        self.startTime = self.getTime_ms()

    # Save the time where player select the grabbing card
    def saveYourTime_ms(self):
        self.yourTime = self.getTime_ms()

    # Save the grabbing card that was selected
    def saveYourGrabbingcard(self, grabbingIndex):
        self.info.yourGrabbingCard = self.cards[grabbedIndex]

    def checkGrabbingAvailable():
        for i in range(len(self.grabbingCardsInPlay)):
            if (self.grabbingCardsInPlay[i].getLastWord() ==
                    self.currentReadingCard.getLastWord()):
                return True
        return False

    # Stupid AI TODO: not validated
    def opponentMove(self):
        takeCorrectCard = False
        random.seed(time.time())
        x = random.uniform(0, 1)
        if (x <= self.parameters.opponentSuccessProb):
            takeCorrectCard = True
        for i in range(len(self.grabbingCardsInPlay)):
            if ((self.grabbingCardsInPlay[i].getLastWord() == self.currentReadingCard.getLastWord()) and \
                (takeCorrectCard)):
                self.info.opponentGrabbingCard = self.grabbingCardsInPlay[i]
                break
            elif ((self.grabbingCardsInPlay[i].getLastWord() != self.currentReadingCard.getLastWord()) and \
                  (not takeCorrectCard)):
                self.info.opponentGrabbingCard = self.grabbingCardsInPlay[i]
                break

        self.info.opponentTime = self.info.startTime + self.parameters.opponentTimeForStupidAI
        self.info.opponentMoved = True

    # TODO: not validated
    def decideWinner(self):
        # Both player grabbed the right card, but you grabbed it faster than opponent
        if ((self.info.yourGrabbingCard == self.currentReadingCard.getLastWord()) and \
            (self.info.opponentGrabbingCard == self.currentReadingCard.getlastWord()) and \
            (self.info.yourTime < self.info.opponentTime)):
            self.info.youWin = True
        # Both player grabbed the right card, but opponent grabbed it faster than you
        elif ((self.info.yourGrabbingCard == self.currentReadingCard.getLastWord()) and \
              (self.info.opponentGrabbingCard == self.currentReadingCard.getlastWord()) and \
              (self.info.yourTime > self.info.opponentTime)):
            self.info.youWin = False
        # you didn't grabbed the right card, but opponent garbbed the right card
        elif ((self.info.yourGrabbingCard != self.currentReadingCard.getLastWord()) and \
              (self.info.opponentGrabbingCard == self.currentReadingCard.getlastWord())):
            self.info.youWin = False
        # you grabbed the right card, but opponent didn't garbbed the right card
        elif ((self.info.yourGrabbingCard == self.currentReadingCard.getLastWord()) and \
              (self.info.opponentGrabbingCard != self.currentReadingCard.getlastWord())):
            self.info.youWin = True
        # if the time pass start time is 18 seconds and it checks that there is no grabbing card match the last word of the currentReadingcard,
        # and both player didn't grabbed any grabbing card, then both player wins
        elif (((self.getTime_ms() - self.startTime) >= 18000) and \
              (checkGrabbingAvailable() is False) and \
              (self.info.yourGrabbingCard == None) and \
              (self.info.opponentGrabbingCard == None)):
            self.info.youWin = True
        # if the time pass start time is 18 seconds and it checks that there is no grabbing card match the last word of the currentReadingcard,
        # and opponent didn't grabbed any grabbing card, but you garbbed a card, then opponent wins
        elif (((self.getTime_ms() - self.startTime) >= 18000) and \
              (checkGrabbingAvailable() is False) and \
              (self.info.yourGrabbingCard != None) and \
              (self.info.opponentGrabbingCard == None)):
            self.info.youWin = True
        # if the time pass start time is 18 seconds and it checks that there is no grabbing card match the last word of the currentReadingcard,
        # and opponentgrabbed a grabbing card, but you didn't grabbed any card, then you wins
        elif (((self.getTime_ms() - self.startTime) >= 18000) and \
              (checkGrabbingAvailable() is False) and \
              (self.info.yourGrabbingCard == None) and \
              (self.info.opponentGrabbingCard != None)):
            self.info.youWin = True

    # The function updates dragIndex, grabbingIndex, mouse, offset
    def selectCard(self, event, dragIndex, grabbingIndex, mouse, offset):
        for j in range(len(self.cards)):
            # If mouse click is on self.cards[j]
            if self.cards[j].collidepoint(event.pos):
                self.cardDragging = (self.phase == Phase.YOUR_SET_UP)
                self.touchYourCard = (j < len(self.cards) // 2)
                mouse.x, mouse.y = event.pos
                dragIndex[0] = j
                grabbingIndex[0] = j
                offset.x = self.cards[dragIndex[0]].x - mouse.x
                offset.y = self.cards[dragIndex[0]].y - mouse.y
                self.cardColors[j] = self.colors.yellow
                if j in self.cardToFrameMap:
                    self.occupied[self.cardToFrameMap[j] -
                                  (len(self.frames) // 2)] = False
                    self.numYourFramesOccupied -= 1
                break

    # The function updates mouse and phase
    def pressDoneButton(self, event, mouse):
        # if the "Done" button was pushed while it is my setup phase, then move onto grabbing phase
        if ((self.doneButton.collidepoint(event.pos)) and \
            (self.phase == Phase.YOUR_SET_UP) and \
            (self.numYourFramesOccupied == (len(self.cards) // 2))):
            self.phase = Phase.DRAWING

    # Draw a reading card
    def drawReadingCard(self):
        if (self.phase == Phase.DRAWING):
            self.currentReadingCard = self.readingCardStack.drawOneCard()
            self.phase == Phase.GRABBING

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
            # TODO Why need this if?
            if (self.phase is Phase.YOUR_SET_UP):
                self.pressDoneButton(event, mouse)
                self.drawReadingCard()
            if (self.phase is Phase.GRABBING):
                self.saveYourTime_ms()
                self.saveYourGrabbingCard(grabbingIndex)

        # The below only works in your set up phase
        elif ((event.type == pygame.MOUSEBUTTONUP) and \
              (event.button == 1)):
            self.cardColors[dragIndex[0]] = self.colors.white
            if (self.cardDragging and self.touchYourCard):
                frameIndex = self.findNearestFrame(
                    Point(self.cards[dragIndex[0]].x,
                          self.cards[dragIndex[0]].y))
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
                self.handleEvent(event, dragIndex, grabbingIndex, mouse,
                                 offset)

            # Rendering
            self.fillScreens()
            self.renderTime()
            self.renderCardFrames()
            if (self.phase is Phase.YOUR_SET_UP):
                self.renderDoneButton()
            self.renderGrabbingCardsAndWords(dragIndex[0])
            # TODO: Why if (phase == GRABBING) does not work here?
            if ((self.phase is Phase.DRAWING)
                    or (self.phase is Phase.GRABBING)):
                self.saveStartTime_ms()
                self.renderReadingCardWords()
                if (self.info.opponentMoved is False):
                    self.opponentMove()
                if (self.getTime_ms() -
                        self.startTime == self.parameters.maxGrabbingTime):
                    if (self.info.yourTime is None):
                        self.saveYourTime_ms()
                    self.decideWinner()

            pygame.display.flip()  # update rendering contents
            self.clock.tick(self.GUIParameters.FPS)

    def quit(self):
        pygame.quit()
