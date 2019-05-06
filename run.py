import sys

if sys.version_info[0] < 3:
    execfile("Cards.py")
else:
    exec (open("Cards.py").read())

if __name__ == "__main__":
    firstWordList = sortFirstWords(READING_CARDS)

    for i in range(len(firstWordList)):
        print(firstWordList[i])
