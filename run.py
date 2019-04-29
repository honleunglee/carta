import sys

if sys.version_info[0] < 3:
    execfile("Cards.py")
else:
    exec (open("Cards.py").read())

if __name__ == "__main__":
    if (len(GRABBING_CARDS) > 0):
        print(GRABBING_CARDS[0].lastWord)
