import csv
from cs50 import SQL


db = SQL("sqlite:///leggi.db")

quotes = []

with open("quotes.csv", "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        quotes.append(row)

print(quotes)

id = 1
for quote in quotes:
    db.execute("INSERT INTO quotes (id, author, quote) VALUES (?, ?, ?)", id, quote["author"], quote["quote"])
    id += 1