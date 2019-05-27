import random
import time

# Fisher-Yates Shuffle
def cardShuffle(cards):
    random.seed(time.time())
    for i in range(len(cards) - 1, 0, -1):
        j = random.randint(0, i)
        cards[i], cards[j] = cards[j], cards[i]
