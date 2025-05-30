# 🧩 Crossword / Word-square Generator 📝

This app can be used to generate rectangular word squares and crosswords.

An external dictionary file is needed, this is not included in the project. Although I tested English language as well, but my main focus was getting Hungarian to work with the full letter set.

## 🕸️ Current State

Please note that I more or less abandoned this project for now. It has reached a minimum working state where I was able to play around with it, but it is still full of bugs and inefficiencies.

I may return to clean this up in the future, but I just wanted to document the current status for now.

## 📜 History

The idea for this project came as I was wondering what is the largest valid word square that could be created using the Hungarian language. I created proof-of-concept custom solver based on the wavefunction collapse algorithm and had positive first results so I stuck with it.

The first version was only a script printing its results into the terminal, but I realized I needed a GUI to be able to more dynamically interact with the solver.

As I had very limited experience with GUI programming, this was also a learning exercise to try and create a ~~dynamic and modern looking~~ working GUI.

## 🧠 Solver

The solver is based on the wavefunction collapse algorithm on a letter level. As a quick summary:

For each cell, the solver counts how many times each letter appears in valid words. Based on this, an entropy is calculated for the cell, reflecting how "uncertain" the cell is. In each step, a final letter is chosen for the most certain cell. If an impossible state is reached, the solver backtracks, and adds the wrong move to a blacklist.
