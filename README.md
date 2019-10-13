# Introduction

Carta is the English PC version of the Japanese game "Competitive Karuta".
It is a two-player game.

# How to install and run the game

It works best if the user's machine has a Unix / Linux system.

For Windows 10 users, you can install a Bash shell command line tool by following the
[instructions](https://www.windowscentral.com/how-install-bash-shell-command-line-windows-10).
You also need [XLaunch](https://seanthegeek.net/234/graphical-linux-applications-bash-ubuntu-windows/)
to run graphical Linux applications.

After that, install Python2 and git via the terminal

```
sudo apt-get install python git
```

and add Python2 to the [enviroment path](https://datatofish.com/add-python-to-windows-path/).

Next, install the Python package pygame via the terminal command

```
sudo apt-get install python-pygame
```

Clone the Carta repository:

```
git clone https://github.com/honleunglee/carta.git
```

To start the game, do the following:

```
cd <path-to-carta-folder>/carta
python run.py
```

# About the game

The game has 100 reading cards and 100 grabbing cards. Each reading card consists of two words.
The words are listed in the file `carta/ReadingCards/ReadingCards.txt`.
If you want to modify the words, please also remove the file
`carta/ReadingCards/ReadingCardsWithDecisionWords.txt`
so that a new and correct file of the same name will be generated.

Grabbing cards exactly have the second words of the reading cards.

# How to play

In this game you will compete with an AI player. At first, each player has 25 grabbing cards.
Both of you need to place all grabbing cards to your side as you like.

In every turn, each of you will be presented the two words of a random reading card,
character by character, at the same time.
Identify the grabbing card that has the second word of the reading card,
and use the mouse to click it faster than the opponent. If such grabbing card does not exist,
do not touch any card.

The touched correct grabbing card will then be removed from play.
Depending on who is the winner and which side the card belongs to,
you may receive a card from your opponent, or you may need to choose a card to give to your opponent.

A wrong grabbing card is either on the opposite side of the correct grabbing card,
or any grabbing card if the correct one is not in play. If you touch a wrong grabbing card
you will be penalized by receiving one card from the opponent.

Repeat this process for multiple turns. At the end, the player who does not have any grabbing cards
on his/her side wins the game.

# Key to win the game: Decision word

Each reading card has a decision word which can be seen in the file
`carta/ReadingCards/ReadingCardsWithDecisionWords.txt`.
Decision word is a part of the first word of a reading card that fully determines
the second word. It means it can fully determine the grabbing card as well.
For example `Star` is the decision word
for the reading card `Starbucks Coffee`. A decent player can grab the grabbing card `Coffee` in play
while `Star` in the reading card is shown.