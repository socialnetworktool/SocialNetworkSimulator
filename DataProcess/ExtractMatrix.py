
import csv
from Tkinter import Tk
from tkFileDialog import askopenfilename

# read data from excel
def ReadData(filepath):
    items = []
    with open(filepath, "r") as fp:
        reader = csv.reader(fp)
        for rows in reader:
            items.append(rows)
    return items

path = "C:\\Users\\Zhuo\\Desktop\\Winter_job\\Twitter-Charlottesville-Search-Data-20171206T021003Z-001\\Twitter-Charlottesville-Search-Data\\"

UserData = ReadData(path + "user_locationid.csv")
UserMADict = {}
for i in range(len(UserData)):
    UserMADict[UserData[i][0]] = [UserData[i][1], UserData[i][2]]

weightMatrix = []
for i in range(26):
    a = []
    for j in range(26):
        a.append(0)
    weightMatrix.append(a)

data = []  # network data to write
Tk().withdraw()
filepath = askopenfilename()
USER_ID_COLUMN = 7 # the index of column of User ID
USER_TEXT_COLUMN = 6 # the index of column of Text
UserFriendsDict = {}

def extract_network(rows):
    users = []  # a list to store clean data
    targets = [word[1:] for word in rows.split() if word.startswith('@') and len(word) > 1]
    # print targets
    if rows.startswith("RT") and len(targets) > 0:
        #print rows
        users.append(targets[0])
    # just process the row that starts with RT@
    # else:
    #     for target in targets:
    #         user = [name for name in target.split("@") if len(name) > 1]
    #         users.extend(user)
    #         # print users
    return users

# Open File and create list of the target column
if filepath != "":
    with open(filepath, "rb") as fp:
        reader = csv.reader(fp)
        for rows in reader:
            #target_col = []
            friends = []
            #target_col.append(rows[USER_ID_COLUMN])
            # if not rows[USER_ID_COLUMN] in UserFriendsDict.keys():
            #     UserFriendsDict[rows[USER_ID_COLUMN]] = set()
            friends_in_row = extract_network(rows[USER_TEXT_COLUMN])
            if not friends_in_row:
                    continue
            for friend in friends_in_row:
                    if "http:" in friend:             # remove "http://..."
                        loc = friend.index("http:")
                        friend = friend[:loc]
                    for syb in "\",?:\\/`*{}[]()>#+-.!$;@":
                            friend = friend.replace(syb, '')  # remove unnecessary symbol after the word
                    friends.append(friend)
            #friends = (", ".join(friends))  # remove brackets []
            # targ_list.append(friends_in_row)
            #friends = friends.split(())
            for i in range(len(friends)):
                #target_col.append(friends[i])
                #data.append(target_col)
                if friends[i] in UserMADict.keys():
                    try:
                        weightMatrix[int(UserMADict[friends[i]][2])][int(UserMADict[rows[USER_ID_COLUMN]][2])] += 1
                    except KeyError as e:
                        print e
                    #UserFriendsDict[rows[USER_ID_COLUMN]].add(friends[i])

# Nodes = {}
# Edges = set()
# for u in UserFriendsDict.keys():
#     friends = UserFriendsDict[u]
#     for f in friends:
#         geo_u = []
#         geo_f = []
#         if u in UserMADict.keys():
#             geo_u = UserMADict[u][1]
#             point = geo_u.lstrip("[").rstrip("]").split(",")
#
#             Nodes[u] = point
#         if f in UserMADict.keys():
#             geo_f = UserMADict[f][1]
#             point = geo_f.lstrip("[").rstrip("]").split(",")
#             Nodes[f] = point
#         data.append([u, geo_u, f, geo_f])
#         if len(geo_u) > 0 and len(geo_f) > 0:
#             Edges.add(str.format("{0}#{1}",u ,f))
#
# # write desired columns to new csv file
# with open("EXTRACTION_RESULT_TEST.csv", 'wb') as fileExtractionResult:
#     writer = csv.writer(fileExtractionResult, delimiter=',')
#     writer.writerows([["USERNAME", "GEOU", "FOLLOWS", "GEOF"]])
#     writer.writerows(data)


with open("C:\\Users\\Zhuo\\Desktop\\WeightMatrix.txt", 'wb') as fileWeightMatrix:
    sequences = []
    for i in range(len(weightMatrix)):
        textStr = ""
        subTotal = 0.0
        for j in range(len(weightMatrix[0])):
            subTotal += weightMatrix[i][j]
        if subTotal > 0:
            for j in range(len(weightMatrix[0])):
                textStr += str(weightMatrix[i][j]/subTotal) + "#"
        else:
            for j in range(len(weightMatrix[0])):
                textStr += "0.0#"
        textStr = textStr.rstrip("#")
        textStr += "\r\n"
        sequences.append(textStr)
    fileWeightMatrix.writelines(sequences)
    fileWeightMatrix.close()
