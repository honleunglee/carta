import sys

if sys.version_info[0] < 3:
    execfile("Cards.py")
    execfile("CardStack.py")
    execfile("CartaUtils.py")
else:
    exec (open("Cards.py").read())
    exec (open("CardStack.py").read())
    exec (open("CartaUtils.py").read())

class Carta:
    def __init__(self, debugMode):
        self.initGame(debugMode)
        self.initRendering()
        self.initReadingCards()
        self.initCardFrames()
        self.initGrabbingCards()

        self.clock = pygame.time.Clock()
        self.running = True  # track if the game is running

    def initGame(self, debugMode):
        pygame.init()
        self.GPinfo = GrabPhaseInfo()
        self.parameters = CartaParameters()
        self.phase = Phase.OPPONENT_SET_UP
        self.debugMode = debugMode

        self.usedGrabbingCards = CardStack([])  # grabbed grabbing card
        self.usedReadingCards = CardStack([])  # read reading card

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
        self.opponentFrames = []
        self.yourFrames = []

        start = Point(self.GUIParameters.leftMargin, self.GUIParameters.topMargin)
        stepX = self.GUIParameters.cardWidth + self.GUIParameters.horizontalSpacing
        for i in range(self.GUIParameters.numCardRows // 2):
            self.setFramesInARow(stepX, start, self.opponentFrames)

        start.y += self.GUIParameters.extraVerticalSpacing  # separation between yours and opponent

        for i in range(self.GUIParameters.numCardRows // 2, self.GUIParameters.numCardRows):
            self.setFramesInARow(stepX, start, self.yourFrames)

        self.occupied = {}
        for frame in self.yourFrames:
            # Note frame is a list which is not hashable, need to convert to tuple
            # which is immutable and then hashable
            self.occupied[tuple(frame)] = False
        self.numYourFramesOccupied = 0

    def initGrabbingCards(self):
        grabbingCardStack = CardStack(GRABBING_CARDS)
        grabbingCardStack.shuffle()
        halfStack = grabbingCardStack.draw(len(GRABBING_CARDS) // 2)

        # constant variables, will not change at run time
        self.yourGrabbingCards = [halfStack[i] for i in range(0, len(halfStack), 2)]
        self.opponentGrabbingCards = [halfStack[i] for i in range(1, len(halfStack), 2)]

        # change at run time. If one of below becomes zero, the corresponding player wins.
        self.numYourGrabCardInPlay = len(self.yourGrabbingCards)
        self.numOppoGrabCardInPlay = len(self.opponentGrabbingCards)

        # First handle your grabbing cards, then opponents
        # Your cards start at the card stack on the right of screen
        for i in range(len(self.yourGrabbingCards)):
            pygameRect = pygame.rect.Rect(self.GUIParameters.stackStart.x, self.GUIParameters.stackStart.y,
                                          self.GUIParameters.cardWidth, self.GUIParameters.cardHeight)
            self.yourGrabbingCards[i].setRect(pygameRect)
            self.yourGrabbingCards[i].setColor(self.colors.white)
            self.yourGrabbingCards[i].setStatus(GrabCardStatus.YOU)

        if (self.phase == Phase.OPPONENT_SET_UP):
            # Opponent cards start at their designated positions
            # For now, assume they are randomly placed
            frameIndexList = [k for k in range(len(self.opponentFrames))]
            # sample len(self.opponentGrabbingCards) indices from len(self.opponentFrames) frames
            random.seed(time.time())
            sampledFrames = random.sample(frameIndexList, self.numOppoGrabCardInPlay)

            for i in range(self.numOppoGrabCardInPlay):
                frame = self.opponentFrames[sampledFrames[i]]
                pygameRect = pygame.rect.Rect(frame[0][0], frame[0][1], self.GUIParameters.cardWidth,
                                              self.GUIParameters.cardHeight)
                card = self.opponentGrabbingCards[i]
                card.setRect(pygameRect)
                card.setColor(self.colors.white)
                card.setStatus(GrabCardStatus.OPPONENT)
                card.setFrame(frame)

            self.phase = Phase.YOUR_SET_UP

        # change at run time
        self.grabbingCardsInPlay = self.yourGrabbingCards + self.opponentGrabbingCards

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
        nearestFrame = None
        # for loop over your frames (not all frames)
        # note: as long as self.yourFrames has no None, this function must return no None
        for frame in self.yourFrames:
            if not self.occupied[tuple(frame)]:
                distSq = (frame[0][0] - pos.x)**2 + (frame[0][1] - pos.y)**2
                if (distSq < minDistanceSq):
                    minDistanceSq = distSq
                    nearestFrame = frame
        return nearestFrame

    def fillScreens(self):
        self.screen.fill(self.colors.lightGreen)
        pygame.draw.rect(self.screen, self.colors.lightBlue, self.infoScreen)

    def renderTime(self):
        timeString = str(self.getIntTime_s())  # in seconds
        timeSurface = self.wordFont.render(timeString, False, self.colors.black)
        self.screen.blit(timeSurface, (self.infoScreen.x + self.GUIParameters.leftTimeMargin,
                                       self.infoScreen.y + self.GUIParameters.topTimeMargin))

    def renderCardFrames(self):
        for frame in self.opponentFrames:
            pygame.draw.lines(self.screen, self.colors.red, True, frame, self.GUIParameters.frameThickness)
        for frame in self.yourFrames:
            pygame.draw.lines(self.screen, self.colors.blue, True, frame, self.GUIParameters.frameThickness)

    def renderSingleCardAndWord(self, card):
        if (card is None):
            return
        pygame.draw.rect(self.screen, card.getColor(), card.getRect())
        textsurface = self.font.render(card.getLastWord(), False, self.colors.black)

        if (card.getStatus() is GrabCardStatus.OPPONENT):
            textsurface = pygame.transform.rotate(textsurface, 180)

        self.screen.blit(
            textsurface,
            (card.getRectX() + self.GUIParameters.leftCardMargin, card.getRectY() + self.GUIParameters.topCardMargin))

    def renderGrabbingCardsAndWords(self, selectedCard):
        # Render cards and write last words on the cards
        # First render the not selected cards
        for i in range(len(self.grabbingCardsInPlay) - 1, -1, -1):
            grabbingCard = self.grabbingCardsInPlay[i]
            if (selectedCard is None):
                self.renderSingleCardAndWord(grabbingCard)
            elif (grabbingCard.sameLastWord(selectedCard) is False):
                self.renderSingleCardAndWord(grabbingCard)

        # Render the selected card, to make sure it is always
        # rendered on top
        self.renderSingleCardAndWord(selectedCard)

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

    # Check if the time between start time and current time at least self.parameters.maxGrabbingTime
    def checkTime(self):
        if ((self.getTime_ms() - self.GPinfo.startTime >= self.parameters.maxGrabbingTime) and \
            (self.GPinfo.timesUp is False)):
            self.GPinfo.timesUp = True

    # Save the starting time of the round
    def saveStartTime_ms(self):
        self.GPinfo.startTime = self.getTime_ms()
        self.GPinfo.savedStartTime = True

    # Save the time where player select the grabbing card
    def saveYourTime_ms(self):
        self.GPinfo.yourTime = self.getTime_ms()

    # Save the grabbing card that you selected
    def saveYourGrabbingCard(self, yourGrabbingCard):
        if ((self.GPinfo.youGrabbedCard is False) and \
            (yourGrabbingCard is not None)):
            self.GPinfo.yourGrabCardLastWord = yourGrabbingCard.getLastWord()
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
        # Both players grabbed the right card, but you grabbed it faster than opponent
        if ((self.GPinfo.yourGrabCardLastWord == self.curReadingCard.getLastWord()) and \
            (self.GPinfo.oppoGrabCardLastWord == self.curReadingCard.getLastWord()) and \
            (self.GPinfo.yourTime < self.GPinfo.opponentTime)):
            self.GPinfo.youWin = True
            self.GPinfo.opponentWin = False
            statement = "Carta.py: decideWinner: Both players grabbed the right card, but you grabbed it faster than opponent"
        # Both players grabbed the right card, but opponent grabbed it faster than you
        elif ((self.GPinfo.yourGrabCardLastWord == self.curReadingCard.getLastWord()) and \
              (self.GPinfo.oppoGrabCardLastWord == self.curReadingCard.getLastWord()) and \
              (self.GPinfo.yourTime > self.GPinfo.opponentTime)):
            self.GPinfo.youWin = False
            self.GPinfo.opponentWin = True
            statement = "Carta.py: decideWinner: Both players grabbed the right card, but opponent grabbed it faster than you"
        # you didn't grab the right card, but opponent grabbed the right card
        elif ((self.GPinfo.yourGrabCardLastWord != self.curReadingCard.getLastWord()) and \
              (self.GPinfo.oppoGrabCardLastWord == self.curReadingCard.getLastWord())):
            self.GPinfo.youWin = False
            statement = "Carta.py: decideWinner: you didn't grab the right card, but opponent grabbed the right card"
        # you grabbed the right card, but opponent didn't grab the right card
        elif ((self.GPinfo.yourGrabCardLastWord == self.curReadingCard.getLastWord()) and \
              (self.GPinfo.oppoGrabCardLastWord != self.curReadingCard.getLastWord())):
            self.GPinfo.youWin = True
            self.GPinfo.opponentWin = False
            statement = "Carta.py: decideWinner: you grabbed the right card, but opponent didn't grab the right card"
        # if the time pass 18 seconds after start time and it checks that there is no grabbing card match the last word of the currentReadingcard,
        # and both players didn't grabbed any grabbing card, then both players win
        elif ((self.GPinfo.timesUp is True) and \
              (self.checkGrabbingAvailable() is False) and \
              (self.GPinfo.yourGrabCardLastWord == "") and \
              (self.GPinfo.oppoGrabCardLastWord == "")):
            self.GPinfo.youWin = True
            self.GPinfo.opponentWin = True
            statement = "Carta.py: decideWinner: No available GrabCard, both players win"
        # if the time pass start time is 18 seconds and it checks that there is no grabbing card match the last word of the currentReadingcard,
        # and opponent didn't grabbed any grabbing card, but you garbbed a card, then opponent wins
        elif ((self.GPinfo.timesUp is True) and \
              (self.checkGrabbingAvailable() is False) and \
              (self.GPinfo.yourGrabCardLastWord != "") and \
              (self.GPinfo.oppoGrabCardLastWord == "")):
            self.GPinfo.youWin = False
            self.GPinfo.opponentWin = True
            statement = "Carta.py: decideWinner: No available GrabCard, opponent win"
        # if the time pass start time is 18 seconds and it checks that there is no grabbing card match the last word of the currentReadingcard,
        # and opponentgrabbed a grabbing card, but you didn't grabbed any card, then you wins
        elif ((self.GPinfo.timesUp is True) and \
              (self.checkGrabbingAvailable() is False) and \
              (self.GPinfo.yourGrabCardLastWord == "") and \
              (self.GPinfo.oppoGrabCardLastWord != "")):
            self.GPinfo.youWin = True
            self.GPinfo.opponentWin = False
            statement = "Carta.py: decideWinner: No available GrabCard, you win"
        else:
            self.GPinfo.youWin = False
            self.GPinfo.opponentWin = False
            statement = "Carta.py: decideWinner: Both players grab wrong card"
        if (self.debugMode):
            print(statement)
        self.GPinfo.ended = True

    # return selectedCard if any
    def selectCard(self, event, mouse, offset):
        selectedCard = None
        # self.grabbingCardsInPLay cannot contain or include None
        for j in range(len(self.grabbingCardsInPlay)):
            # If mouse click is on self.grabbingCardsInPlay[j].getRect()
            if self.grabbingCardsInPlay[j].getRect().collidepoint(event.pos):
                self.cardDragging = (self.phase == Phase.YOUR_SET_UP)
                mouse.x, mouse.y = event.pos
                selectedCard = self.grabbingCardsInPlay[j]
                self.touchYourCard = (selectedCard.getStatus() is GrabCardStatus.YOU)
                offset.x = selectedCard.getRectX() - mouse.x
                offset.y = selectedCard.getRectY() - mouse.y
                selectedCard.setColor(self.colors.yellow)
                if ((selectedCard.getFrame() is not None) and self.touchYourCard):
                    # self.occupied is only about your side.
                    self.occupied[tuple(selectedCard.getFrame())] = False
                    self.numYourFramesOccupied -= 1
                break
        return selectedCard

    # only run at initialization
    def randomAssignYourGrabCards(self):
        frameIndexList = [k for k in range(len(self.yourFrames))]

        # self.numYourGrabCardInPlay indices from len(self.yourFrames) frames
        random.seed(time.time())
        sampledFrames = random.sample(frameIndexList, self.numYourGrabCardInPlay)

        for i in range(self.numYourGrabCardInPlay):
            frame = self.yourFrames[sampledFrames[i]]
            pygameRect = pygame.rect.Rect(frame[0][0], frame[0][1], self.GUIParameters.cardWidth,
                                          self.GUIParameters.cardHeight)
            card = self.yourGrabbingCards[i]
            card.setRect(pygameRect)
            card.setFrame(frame)
            if tuple(frame) in self.occupied:
                self.occupied[tuple(frame)] = True
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

    # return selected Card if any
    def handleEvent(self, event, selectedCard, mouse, offset):
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
            selectedCard = self.selectCard(event, mouse, offset)
            if (self.phase is Phase.GRABBING):
                self.saveYourTime_ms()
                self.saveYourGrabbingCard(selectedCard)
            if (self.phase == Phase.YOUR_SET_UP):
                self.pressDoneButton(event, mouse)
                self.drawReadingCard()

        # The below only works in your set up phase
        elif ((event.type == pygame.MOUSEBUTTONUP) and \
              (event.button == 1) and \
              (selectedCard is not None)):
            selectedCard.setColor(self.colors.white)
            if (self.cardDragging and self.touchYourCard):
                frame = self.findNearestFrame(selectedCard.getPos())
                selectedCard.setRectX(frame[0][0])
                selectedCard.setRectY(frame[0][1])
                selectedCard.setFrame(frame)
                self.occupied[tuple(frame)] = True
                self.numYourFramesOccupied += 1

                self.cardDragging = False
                self.touchYourCard = False

        # Left click and drag your card
        elif ((event.type == pygame.MOUSEMOTION) and \
              self.cardDragging and \
              self.touchYourCard and \
              (selectedCard is not None)):
            mouse.x, mouse.y = event.pos
            selectedCard.setRectX(mouse.x + offset.x)
            selectedCard.setRectY(mouse.y + offset.y)

        return selectedCard

    def process(self):
        selectedCard = None
        # record mouse position relative to left top corner of the whole screen
        mouse = Point(0, 0)
        # record left top corner of the selected card relative to mouse position
        offset = Point(0, 0)
        while self.running:
            for event in pygame.event.get():
                selectedCard = self.handleEvent(event, selectedCard, mouse, offset)
            self.fillScreens()
            self.renderTime()
            self.renderCardFrames()
            if (self.phase is Phase.YOUR_SET_UP):
                if (self.debugMode and self.yourGrabCardAssigned is False):
                    self.randomAssignYourGrabCards()
                self.renderDoneButton()
            self.renderGrabbingCardsAndWords(selectedCard)
            if (self.displayReadingCard):
                if (self.GPinfo.savedStartTime is False):
                    self.saveStartTime_ms()
                self.checkTime()
                self.renderReadingCardWords()
                if (self.GPinfo.oppoGrabbedCard is False):
                    self.opponentGrabsCard()
                if ((self.GPinfo.ended is False) and (self.GPinfo.timesUp is True)):
                    if (self.GPinfo.yourTime is None):
                        self.saveYourTime_ms()
                    self.decideWinner()

            pygame.display.flip()  # update rendering contents
            self.clock.tick(self.GUIParameters.FPS)

    def quit(self):
        pygame.quit()
