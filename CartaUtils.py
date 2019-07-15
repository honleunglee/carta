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
        self.ended = False
        self.youGrabbedCard = False
        self.youWin = False
        self.opponentWin = False

class CartaParameters:  # constant parameters
    def __init__(self):
        self.opponentTimeForStupidAI = 10000  # ms
        self.maxGrabbingTime = 18000  # ms
        self.opponentSuccessProb = 0.8
