import sys

if sys.version_info[0] < 3:
    execfile("Carta.py")
else:
    exec (open("Carta.py").read())

if __name__ == "__main__":
    debugMode = False
    if (len(sys.argv) > 1):
        if (sys.argv[1].lower() == "debug"):
            debugMode = True

    c = Carta(debugMode)
    c.process()
    c.quit()
