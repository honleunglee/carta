import sys

if sys.version_info[0] < 3:
    execfile("Cards.py")
    execfile("CardStack.py")
else:
    exec (open("Cards.py").read())
    exec (open("CardStack.py").read())

if __name__ == "__main__":
    pass
