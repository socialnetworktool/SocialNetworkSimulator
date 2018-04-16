import csv
import os
from datetime import datetime


def SplitExcelFile(filePath):
    count = 0
    fileindex = 0
    filename = "N_" + filePath.rstrip(".csv") + str(fileindex) + ".csv"
    fWrite = open(filename, "a")
    strTitle = ""
    with open(filePath) as f:
        for line in f:
            count += 1
            fWrite.write(line)
            if line.find("\r\n") != -1:
                print line
            if count == 1:
                strTitle = line
            if count % 1000000 == 0:
                fWrite.close()
                fileindex += 1
                filename = "N_" + filePath.rstrip(".csv") + str(fileindex) + ".csv"
                fWrite = open(filename, "a")
                fWrite.write(strTitle)
        fWrite.close()
        print count


def ReadCSV(filePath):
    items = []
    count = 0
    with open(filePath) as f:
        reader = csv.DictReader(f)

        for row in reader:
            items.append([row["user.screen_name"], row["geo.coordinates"], row["text"], row["created_at_local"]])
            # count += 1
            # print filePath, count
            # if row["text"].find("\r\n") != -1:
            #     print row["text"]
    return items


def ReadFileByBite(filePath):
    f = open(filePath, "rb")
    a = ""
    try:
        byte = f.read(1)
        while byte != "":
            byte = f.read(1)
            a += byte
    finally:
        print a
        f.close()


def FollowExtractByAtSymbol(items, relationship):
    for i in range(len(items)):
        tweet = items[i][2]
        tag = set()
        tag = GetBySymbol(tweet, tag, "@")
        for user in tag:
            relationship[items[i][0]].add(user)
    return relationship


def FollowExtractByHashtag(items, relationship, deltaT):
    for i in range(len(items)):
        tag = set()
        tag = GetBySymbol(items[i][2], tag, "#")
        items[i].append(tag)

    for i in range(len(items)):
        userName1 = items[i][0]
        tweetTime1 = GetTime(items[i][3])
        tag1 = items[i][4]
        for j in range(i + 1, len(items)):
            tweetTime2 = GetTime(items[j][3])
            userName2 = items[j][0]
            tag2 = items[j][4]
            if DeltaTime(tweetTime2, tweetTime1) <= deltaT:
                if userName1 != userName2:
                    if tag1 == tag2:
                        relationship[userName1].add(userName2)
            else:
                break
    return relationship


def GetBySymbol(strTweet, tag, symbol):
    tag.clear()
    while True:
        index = strTweet.find(symbol)
        _tag = ""
        if index != -1:
            index += 1
        else:
            break
        while index < len(strTweet):
            if strTweet[index] != " ":
                _tag += strTweet[index]
                index += 1
            else:
                if index < len(strTweet) - 1:
                    strTweet = strTweet[index + 1:len(strTweet)]
                else:
                    strTweet = ""
                break
        tag.add(_tag)
        if index == len(strTweet):
            break
    print "TAG:", tag
    return tag

def GetTime(strDate):
    strDate = strDate.replace("T", " ")
    strDate = strDate.replace("Z", " ")
    strDate = str(strDate).split(".")[0]
    return datetime.strptime(strDate, '%Y-%m-%d %H:%M:%S')


def DeltaTime(a, b):
    delta = a - b
    return delta.days * 3600 * 24 + delta.seconds


if __name__ == "__main__":
    items = []

    # ReadFileByBite("C:\\Users\\GISer\\Desktop\\Tweets_SanDiego2015\\New Microsoft Excel Worksheet.csv")

    tag = False
    if tag:
        path = "C:\\Users\\GISer\\Desktop\\Tweets_SanDiego2015"
        files = os.listdir(path)
        os.chdir(path)
        for f in files:
            print f
            SplitExcelFile(f)
    else:
        path = "C:\\Users\\GISer\\Desktop\\Tweets_SanDiego2015\\new"
        files = os.listdir(path)
        os.chdir(path)
        count = 0
        for f in files:
            print f
            items = []
            items.extend(ReadCSV(f))
            print len(items)
            relationship = {}
            for i in range(len(items)):
                relationship[items[i][0]] = set()
            FollowExtractByAtSymbol(items, relationship)
            #FollowExtractByHashtag(items, relationship, 60)

            filename = "friends.csv"
            f = open(filename, "a+")

            for key in relationship.keys():
                if len(relationship[key]) > 0:
                    for u in relationship[key]:
                        f.write(str.format("{0},{1}\n", key, u))
                        count += 1
            f.close()
        print "just @: ", count
            # dictUser = {}
            # for item in items:
            #     geo = item[1]
            #     key = item[0]
            #     if dictUser.has_key(key):
            #         if geo != "" and str(dictUser[key][0]).find(geo) == -1:
            #             if dictUser[key][0] != "":
            #                 dictUser[key] = [dictUser[key][0] + ";" + geo, dictUser[key][1] + 1]
            #             else:
            #                 dictUser[key] = [geo, dictUser[key][1] + 1]
            #         else:
            #             dictUser[key] = [dictUser[key][0], dictUser[key][1] + 1]
            #     else:
            #         dictUser[key] = [geo, 1]
            # print len(dictUser)
            #
            # count = 0
            # count1 = 0
            # count2 = 0
            # count3 = 0
            # count4 = 0
            # outtweets = []
            # outtweets1 = []
            # for key in dictUser.keys():
            #     if dictUser[key][0] == "":
            #         count += 1
            #         count1 += dictUser[key][1]
            #         outtweets.append([key, dictUser[key][1]])
            #     else:
            #         count2 += 1
            #         geos = dictUser[key][0].split(";")
            #         count3 += len(geos)
            #         count4 += dictUser[key][1]
            #         outtweets1.append([key, len(geos), dictUser[key][1]])
            # print count, count1, count2, count3, count4
            #
            # with open('NoGeoTwets.csv', 'wb') as f:
            #     writer = csv.writer(f)
            #     writer.writerow(["user_screenname", "n_tweets"])
            #     writer.writerows(outtweets)
            #     f.close()
            #
            # with open('GeoTweets.csv', 'wb') as f:
            #     writer = csv.writer(f)
            #     writer.writerow(["user_screenname", "n_geo", "n_tweets"])
            #     writer.writerows(outtweets1)
            #     f.close()
