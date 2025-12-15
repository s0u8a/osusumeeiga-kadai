import csv

# movies
with open("movies_100k.csv", encoding="latin-1") as f, \
     open("movies_fixed.csv", "w", encoding="utf-8", newline="") as out:
    reader = csv.reader(f, delimiter="|")
    writer = csv.writer(out)
    for row in reader:
        writer.writerow(row)

# ratings
with open("ratings_100k.csv", encoding="latin-1") as f, \
     open("ratings_fixed.csv", "w", encoding="utf-8", newline="") as out:
    reader = csv.reader(f, delimiter="\t")
    writer = csv.writer(out)
    for row in reader:
        writer.writerow(row)

print("OK")
