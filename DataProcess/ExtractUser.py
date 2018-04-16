import csv

# read data from excel
def ReadData(filepath):
    data = []
    with open(filepath, "r") as fp:
        reader = csv.reader(fp, dialect=csv.excel)
        for rows in reader:
            data.append(rows)
    return data

path = "C:\\SocialNetworkSimulator\\Tweets\\Vaccine\\"

MAData = ReadData(path + "TOP30MAPoints.csv")
MADict = {}
for i in range(1, len(MAData)):
    MADict[MAData[i][4]] = MAData[i][8] #str.format("[{0},{1}]", MAData[i][10], MAData[i][11])

vaccineTweets = ReadData(path + "vaccine_05252015_05312016_TOP30.csv")


MA_NAME_TITLE = "NAME"
CreateTime_TITLE = "created_at"
UserName_TITLE = "user_scree"
TEXT_TITLE = "text"

Tweets_Dict_TIME_MA = {}
User_Dict = {}

t_index = vaccineTweets[0].index(CreateTime_TITLE)
ma_index = vaccineTweets[0].index(MA_NAME_TITLE)
u_index = vaccineTweets[0].index(UserName_TITLE)
text_index = vaccineTweets[0].index(TEXT_TITLE)

for i in range(1, len(vaccineTweets)):
    print vaccineTweets[i][0]
    if vaccineTweets[i][ma_index] == "":
        continue
    User_Dict[vaccineTweets[i][u_index]] = [vaccineTweets[i][ma_index], MADict[vaccineTweets[i][ma_index]]]

test = open(path + "UserResult" + ".txt", 'a')

s = ""
for key in User_Dict.keys():
    s += key + ";" + User_Dict[key][0] + ";" + User_Dict[key][1] + "\r\n"
test.write(s)
test.close()



