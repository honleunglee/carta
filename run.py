import sys

if sys.version_info[0] < 3:
    execfile("Cards.py")
else:
    exec (open("Cards.py").read())

if __name__ == "__main__":
    analyzeCards(READING_CARDS, GRABBING_CARDS)
