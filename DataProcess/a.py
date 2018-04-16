import csv

def ReadCSV(filePath):
    count = 0
    reader = csv.reader(filePath)
    for row in reader:
        count += 1
    return count

if __name__ == "__main__":
    items = []

    # ReadFileByBite("C:\\Users\\GISer\\Desktop\\Tweets_SanDiego2015\\New Microsoft Excel Worksheet.csv")

    print ReadCSV("C:\\Users\\GISer\\Desktop\\Tweets_SanDiego2015\\new\\friends.csv")

