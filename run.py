import sys

if sys.version_info[0] < 3:
    execfile("Carta.py")
else:
    exec (open("Carta.py").read())

if __name__ == "__main__":
    c = Carta()
    c.process()
    c.quit()
