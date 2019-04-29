execfile("Cards.py")

if __name__ == "__main__":
    if (len(GRABBING_CARDS) > 0):
        print(GRABBING_CARDS[0].lastWord)
