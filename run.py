import sys
import Carta

if __name__ == "__main__":
    debugMode = False
    if (len(sys.argv) > 1):
        if (sys.argv[1].lower() == "debug"):
            debugMode = True

    # First Carta means Carta.py, second Carta means class name Carta
    c = Carta.Carta(debugMode)
    c.process()
    c.quit()
