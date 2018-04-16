import csv
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
    MADict[MAData[i][4]] = MAData[i][8]

strData = "2015-06-28"
path = "C:\\SocialNetworkSimulator\\Tweets\\Vaccine\\"
vaccineTweets = ReadData(path + "vaccine_05252015_05312016_TOP30.csv")

MA_NAME_TITLE = "NAME"
CreateTime_TITLE = "created_at"
UserName_TITLE = "user_scree"
TEXT_TITLE = "text"

t_index = vaccineTweets[0].index(CreateTime_TITLE)
ma_index = vaccineTweets[0].index(MA_NAME_TITLE)
u_index = vaccineTweets[0].index(UserName_TITLE)
text_index = vaccineTweets[0].index(TEXT_TITLE)

MATweetsDict = {}
for key in MADict.keys():
    MATweetsDict[MADict[key]] = 0

for i in range(1, len(vaccineTweets)):
    if vaccineTweets[i][t_index][0:10] != strData:
        continue
    if vaccineTweets[i][ma_index] == "":
        continue
    MATweetsDict[MADict[vaccineTweets[i][ma_index]]] += 1

test = open(path + "CurrentStatus" + ".txt", 'a')

s = ""
for key in MATweetsDict.keys():
    s += key + "#" + str(MATweetsDict[key]) + "\r\n"
test.write(s)
test.close()


