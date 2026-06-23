import csv

file = open("airport-codes_csv.csv", encoding="utf-8")

reader = csv.DictReader(file, delimiter=";")

for row in reader:
    if row["iso_country"] == "UA":
        print(row["name"])

file.close()