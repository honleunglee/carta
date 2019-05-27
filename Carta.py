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
        self.numFrames = 72  # card frames (number of frames per row * self.numCardRows)
        self.frameThickness = 3
        self.horizontalSpacing = 1  # between two frames
        self.verticalSpacing = 10  # between two rows of frames
        self.extraVerticalSpacing = self.verticalSpacing * 2
        self.fontSize = 18
        self.numCardRows = 6
        self.leftMargin = 20  # for grabbing cards in the screen
        self.topMargin = 20  # for grabbing cards in the screen
        self.infoScreenStartX = self.screenWidth * 7 // 10
        self.stackStart = Point(
            750, 400)  # left top point for stack of grabbing cards
        self.leftCardMargin = 5  # for last word in a grabbing card
        self.topCardMargin = 5  # for last word in a grabbing card

class Carta:
    def __init__(self):
        pygame.init()

        self.initRendering()
        self.initGrabbingCards()
        self.initCardFrames()

        self.clock = pygame.time.Clock()
        self.running = True  # track if the game is running

    def initRendering(self):
        self.colors = Colors()
        self.GUIParameters = GUIParameters()
        self.screen = pygame.display.set_mode(
            (self.GUIParameters.screenWidth, self.GUIParameters.screenHeight))
        pygame.display.set_caption("Carta")

        pygame.font.init()
        self.font = pygame.font.SysFont('freesans',
                                        self.GUIParameters.fontSize)

        self.infoScreen = pygame.rect.Rect(
            self.GUIParameters.infoScreenStartX, 0,
            self.GUIParameters.screenWidth -
            self.GUIParameters.infoScreenStartX,
            self.GUIParameters.screenHeight)

    def initGrabbingCards(self):
        # To fix: should be 25 cards for you, 25 cards for opponent
        self.lastWords = [card.lastWord for card in GRABBING_CARDS]
        # grabbing cards as rectangles in screen
        self.cards = [None] * len(self.lastWords)
        self.cardColors = [self.colors.white] * len(self.lastWords)
        for i in range(len(self.cards)):
            self.cards[i] = pygame.rect.Rect(self.GUIParameters.stackStart.x,
                                             self.GUIParameters.stackStart.y,
                                             self.GUIParameters.cardWidth,
                                             self.GUIParameters.cardHeight)
        self.cardDragging = False

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

    def createCardFrame(self, lt):
        rb = Point(lt.x + self.GUIParameters.cardWidth,
                   lt.y + self.GUIParameters.cardHeight)
        return [(lt.x, lt.y), (lt.x, rb.y), (rb.x, rb.y), (rb.x, lt.y)]

    # pos is the position of left top corner of a card
    def findNearestFrame(self, pos):
        minDistanceSq = sys.float_info.max
        bestFrameIndex = self.GUIParameters.numFrames
        # for loop over your frames (not all frames)
        # TODO(Chapman): Only consider unoccupied frames
        for i in range(self.GUIParameters.numFrames // 2,
                       self.GUIParameters.numFrames):
            distSq = (self.frames[i][0][0] - pos.x)**2 + \
                     (self.frames[i][0][1] - pos.y)**2
            if (distSq < minDistanceSq):
                minDistanceSq = distSq
                bestFrameIndex = i
        return bestFrameIndex

    def fillScreens(self):
        self.screen.fill(self.colors.lightGreen)
        pygame.draw.rect(self.screen, self.colors.lightBlue, self.infoScreen)

    def drawCardFrames(self):
        for j in range(len(self.frames) // 2):
            pygame.draw.lines(self.screen, self.colors.red, True,
                              self.frames[j],
                              self.GUIParameters.frameThickness)
        for j in range(len(self.frames) // 2, len(self.frames)):
            pygame.draw.lines(self.screen, self.colors.blue, True,
                              self.frames[j],
                              self.GUIParameters.frameThickness)

    def drawCardsAndWords(self):
        # Draw cards and write last words on the cards
        for i in range(len(self.cards)):
            pygame.draw.rect(self.screen, self.cardColors[i], self.cards[i])
            textsurface = self.font.render(self.lastWords[i], False,
                                           self.colors.black)
            self.screen.blit(
                textsurface,
                (self.cards[i].x + self.GUIParameters.leftCardMargin,
                 self.cards[i].y + self.GUIParameters.topCardMargin))

    # The function updates dragIndex, mouse, offset
    def selectCard(self, event, dragIndex, mouse, offset):
        for j in range(len(self.cards)):
            # If mouse click is on self.cards[j]
            if self.cards[j].collidepoint(event.pos):
                self.cardDragging = True
                mouse.x, mouse.y = event.pos
                dragIndex[0] = j
                offset.x = self.cards[dragIndex[0]].x - mouse.x
                offset.y = self.cards[dragIndex[0]].y - mouse.y
                self.cardColors[j] = self.colors.yellow
                break

    # The function updates dragIndex, mouse, offset
    def handleEvent(self, event, dragIndex, mouse, offset):
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
            self.selectCard(event, dragIndex, mouse, offset)

        elif ((event.type == pygame.MOUSEBUTTONUP) and \
              (event.button == 1) and \
               self.cardDragging):
            frameIndex = self.findNearestFrame(
                Point(self.cards[dragIndex[0]].x, self.cards[dragIndex[0]].y))

            self.cards[dragIndex[0]].x = self.frames[frameIndex][0][0]
            self.cards[dragIndex[0]].y = self.frames[frameIndex][0][1]
            self.cardColors[dragIndex[0]] = self.colors.white
            self.cardDragging = False

        # Left click and drag the mouse
        elif ((event.type == pygame.MOUSEMOTION) and self.cardDragging):
            mouse.x, mouse.y = event.pos
            self.cards[dragIndex[0]].x = mouse.x + offset.x
            self.cards[dragIndex[0]].y = mouse.y + offset.y

    def process(self):
        dragIndex = [0]  # index of the card being dragged
        # record mouse position relative to left top corner of the whole screen
        mouse = Point(0, 0)
        # record left top corner of the dragging card relative to mouse position
        offset = Point(0, 0)
        while self.running:
            for event in pygame.event.get():
                self.handleEvent(event, dragIndex, mouse, offset)

            # Rendering
            self.fillScreens()
            self.drawCardFrames()
            self.drawCardsAndWords()

            pygame.display.flip()  # update drawing contents
            self.clock.tick(self.GUIParameters.FPS)

    def quit(self):
        pygame.quit()
