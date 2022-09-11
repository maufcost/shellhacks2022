# read a big csv file
import csv
import os


# write a function that reads a csf file and returns a list of dictionaries
# each dictionary is a row in the csv file
# the header row is the key for each dictionary
def read_csv_file(filename):
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        return list(reader)

all_objs = read_csv_file("security.csv")
file_out = open("security.txt", "w")
for obj in all_objs:
    file_out.write(str(obj) + ",\n")
file_out.close()