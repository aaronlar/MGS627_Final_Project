#this is all of the stuff that I have done with the Riot API so far and hopefully soon I make the dream come true of
#getting win rates as far as I can go

#I am going to use the Riot Games API to attempt to graph my top 10 characters in League of Legends
#based on my mastery points
#importing the required packages and libraries to run the code
import requests
import pandas as pd
import matplotlib.pyplot as plt
#this is all the information that needs to be provided so the player can be identified and the
#api requests won't be denied
#my Riot API Key
api_key = 'my api kay'
#My name in League of Legends
gameName = 'Volani'
#region I play in
region = 'NA1'
#the tagline on my account
tagline = 'NA1'
#establish a header to use with my API requests to use my API key, and to prevent having to type
#or concat the api key to every url
headers = {"X-Riot-Token":api_key}
#making a function for doing quick error checking to make sure that my api requests are working
def errorHandlingForRequests(response):
    """
    This function does small error checking for requests to make sure that the request went through properly and if it did
    not it prints out the HTTP error code to diagnose the issue
    :param response: the requests module response after running a requests.get() on a URL
    :return: a print statement with the HTTP error code to diagnose the issue
    """
    if response.status_code != 200:
        print('error: ', response.status_code)

#Data Dragon is name that Riot games gives to its repositories or data related to League of Legends
#I am making a request to the url for champion.json in order to get all of the champion data so I can
#relate championID's in other information about the champions
champDataUrl = 'https://ddragon.leagueoflegends.com/cdn/14.19.1/data/en_US/champion.json'
#making a function to get the names of champions in a dictionary
def getChampionData(upToDateDataDragonURL):
    """
    This function sends a request to the provided url that should be the most up to date version of the Data Dragon for
    League of Legends in order to get a dictionary that contains the championID's as keys and the champion names as
    values
    :param upToDateDataDragonURL: the url of the Data Dragon that is up to date with the most recent patch of
    League of Legends
    :return: a dictionary that contains the championID's as integers as the keys and the champions names
    as strings as the values
    """
    #send the request
    champDataResponse = requests.get(upToDateDataDragonURL)
    #error checking with function
    errorHandlingForRequests(champDataResponse)
    #json decoding
    champDataJSON = champDataResponse.json()
    #extracting just the data about champions from the response
    champData = champDataJSON['data']
    #make a dictionary to store champion ids and map them to names
    champNames = {}
    #Loop over the data about champions to just get the champion id's as ints and the names as strings
    for name, details in champData.items():
        #get champ id and make it an int
        champID = int(details['key'])
        #add the champ id as a key in champion name dictionary and add the champion name as its value
        champNames[champID] = name
    #checking that I have a name for every champ in the game as of the latest patch for the game there is 168
    #as of 10/4/2024
    if len(champNames) == 168:
        return champNames
    else:
        print('the number of champions is incorrect, please double check the version of the Data Dragon you are using')
#calling the function
champNames = getChampionData(champDataUrl)

#making a function to get the 'puuid' associated with my account, this is a more unique
#identifier for accounts that is often used to make other API requests
def getPuuid():
    """
    this function gets the 'puuid' associated with the account details at the beginning of the file, this is a more unique
    identifier for accounts that is often used to make other API requests
    :return: returns the puuid associated with the account details provided at the top of the file
    """
    #making the full URL to get more details about my account
    accountUrl = 'https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/'+gameName+'/'+tagline
    #sending a request to the API with my summoner name to get more details about my account
    accountResponse  = requests.get(accountUrl, headers=headers)
    #error handling with function
    errorHandlingForRequests(accountResponse)
    #json decoding
    accountDetails = accountResponse.json()
    #a new unique identifier for my account that makes it easier for me to use the api to find data about my account
    puuid = str(accountDetails['puuid'])
    return puuid
#calling the function
puuid = getPuuid()

#making a function that sends an API request to get information on Champion Mastery for the account
#provided at the beginning and formats the information into dictionary
def getChampMastery():
    """
    this function sends an API request to get information on Champion Mastery for the account
    provided at the beginning using the puuid for the account and formats the information into dictionary
    :return: a dictionary that contains the Mastery Points value for every champion that has mastery points
    as the values in a dictionary and the keys are the names of the champions
    """
    #assemble the url
    champMasteryUrl = 'https://'+region+'.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/'+puuid
    #sending the request
    champMasteryResponse = requests.get(champMasteryUrl, headers=headers)
    #error handling with function
    errorHandlingForRequests(champMasteryResponse)
    #json decoding
    champMasteryData = champMasteryResponse.json()
    #creating an empty dictionary to store just the champion mastery points and the name of the champion
    #the player has the points with
    champMasteryWithNames = {}
    #Filling out the dictionary with names of champions and their mastery points
    for champion in champMasteryData:
        championID = champion['championId']
        champIDToName = champNames.get(championID,"unknown")
        champMasteryWithNames[champIDToName] = champion['championPoints']
    return champMasteryWithNames
#calling the function
champMasteryWithNames = getChampMastery()

#making a function to convert the champMasteryWithNames dictionary into 2 lists that are then used
#as values in a separate dictionary that is then used to make a pandas dataframe which is
# saved as a .csv file and used to make an informative statement about the data contained within it
def informativeStatement(champMasteryDict):
    """
    this function converts the champMasteryWithNames dictionary into 2 lists that are then used
    as values in a separate dictionary that is then used to make a pandas dataframe which is
    saved as a .csv file and used to make an informative statement about the data contained within it
    :param champMasteryDict: this is the output of the getChampMastery function
    :return: a print statement containing an informative statement about the data within the dataframe that is created
    the pandas dataframe that is created and saved as a .csv file
    """
    #making a list to store just names for a dictionary to make the data frame
    champNameList = []
    #making a list to store just the mastery points to make the data frame
    champMasteryList = []
    #loop over the dictionary to append all of the names to the list
    for name in champMasteryDict.keys():
        champNameList.append(name)
    #looping over the dictionary to append all of the Mastery point values to the list
    for mastery in champMasteryDict.values():
        champMasteryList.append(mastery)
    #creating the dictionary for making the data frame
    dataForDataFrame = {'Champion Names':champNameList, 'Champion Mastery': champMasteryList}
    #creating the dataframe
    champMasteryDataFrame = pd.DataFrame(dataForDataFrame)
    #saving the dataframe to a csv file
    champMasteryDataFrame.to_csv('VolaniiChampionMastery.csv')
    #identifing the maximum number of mastery points I have on a champion
    maxMasteryPoints = str(champMasteryDataFrame['Champion Mastery'].max())
    #getting the index of the highest number of mastery points
    maxMasteryIndex = champMasteryDataFrame['Champion Mastery'].idxmax()
    #using the index of the highest number of champion to get the name of the champion with the highest number of mastery
    #points
    championWithMaxMastery = str(champMasteryDataFrame.loc[maxMasteryIndex, 'Champion Names'])
    #printing an informative statement about the maximum value of mastery points and the champion with the highest number
    #of mastery points of the player name used
    print('The Champion that ' +gameName+ ' has the most mastery points on is ' +championWithMaxMastery+
          ' the amount of of Mastery Points on ' +championWithMaxMastery+ ' is ' +maxMasteryPoints)
    return champMasteryDataFrame
#calling the function
champMasteryDataFrame = informativeStatement(champMasteryWithNames)
#making a function to just capture the top 10 champions in the pandas dataframe and then graph them using matplotlib
def graphMax10(champMasteryDataFrame):
    """
    a function to capture the top 10 champions in a pandas dataframe created in the informativeStatement function
    and then graph them using matplotlib
    :param champMasteryDataFrame: this is the dataframe output of informtativeSatement
    :return: a matplotlib graph that shows the mastery points of the 10 champions that have the most
    mastery points for the account specified at the beginning
    """
    #making a new dataframe that only includes the top 10 champions by Mastery Points
    max10Champs = champMasteryDataFrame.sort_values(by='Champion Mastery', ascending=False).head(10)
    #graphing, in order to make the graph is useful and is actually graphing the mastery points of each champion I am
    #leaning on some prior experience with matplotlib to make the graph I actually want
    #making the axis
    xAxis = max10Champs['Champion Names']
    yAxis = max10Champs['Champion Mastery']
    #making it a bar graph
    plt.bar(xAxis,yAxis)
    #adding labels
    plt.xlabel('Champion Names')
    plt.ylabel('Mastery Points')
    #titling the graph
    plt.title(gameName + "'s Top 10 Highest Mastery Point Champions")
    #showing the graph
    plt.tight_layout()
    plt.show()
#calling the function
graphMax10(champMasteryDataFrame)
def getrecentmatchhistory(puuid):
    #grabbing the last 20 matches matchID to get more information from them
    matchURL = 'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/'+puuid+'/ids?start=0&count=20&'
    matchResponse = requests.get(matchURL, headers=headers)
    matches = matchResponse.json()
    return matches
recent_match_history = getrecentmatchhistory(puuid)
def get_match_info(matchID):
    #getting all of the data based on the match id used
    matchInfoUrl ='https://americas.api.riotgames.com/lol/match/v5/matches/'+matchID
    matchInfoResponse = requests.get(matchInfoUrl, headers=headers)
    matchInfo = matchInfoResponse.json()
    return matchInfo
match_info = get_match_info(recent_match_history[0])

def get_player_info_from_puuid(puuid, match_info):
    participant_info = next((
        participant for participant in match_info['info']['participants'] if participant['puuid'] == puuid), None)
    return participant_info
participant_info = get_player_info_from_puuid(puuid, match_info)
def make_sure_participant_info_is_real(participant_info):
    if participant_info != participant_info:
        print('participant does not exist')
make_sure_participant_info_is_real(participant_info)
def make_damage_graph(participant_info):
    fig, ax = plt.subplots()
    ax.bar(participant_info['championName'], participant_info["physicalDamageTaken"],
        label='Physical Damage Taken ' + str(participant_info['physicalDamageTaken']), color='orange')
    ax.bar(participant_info['championName'], participant_info["magicDamageTaken"],
        bottom=participant_info["physicalDamageTaken"],
        label='Magic Damage Taken ' + str(participant_info['magicDamageTaken']), color='b')
    ax.bar(participant_info['championName'], participant_info['trueDamageTaken'],
        bottom=participant_info['physicalDamageTaken'] + participant_info['magicDamageTaken'],
        label='True Damage Taken ' + str(participant_info['trueDamageTaken']), color='silver')
    ax.legend()
    plt.title(gameName + ' Damage Taken')
    plt.show()
def make_damage_graphs(ax, row, col, participant_info):
    ax[row, col].bar(participant_info['championName'], participant_info["physicalDamageTaken"],
           label='Physical Damage Taken ' + str(participant_info['physicalDamageTaken']), color='orange')
    ax[row, col].bar(participant_info['championName'], participant_info["magicDamageTaken"],
           bottom=participant_info["physicalDamageTaken"],
           label='Magic Damage Taken ' + str(participant_info['magicDamageTaken']), color='b')
    ax[row, col].bar(participant_info['championName'], participant_info['trueDamageTaken'],
           bottom=participant_info['physicalDamageTaken'] + participant_info['magicDamageTaken'],
           label='True Damage Taken ' + str(participant_info['trueDamageTaken']), color='silver')
    ax.legend()
    ax.set_title(participant_info['championName'] + ' Damage Taken')

# List of all participants' puuids
puuids = [participant['puuid'] for participant in match_info['info']['participants']]

# Create a 2x5 subplot
fig, axs = plt.subplots(2, 5, figsize=(20, 10))

# Iterate over the participants and create graphs
for puuid in puuids:
    participant_info = get_player_info_from_puuid(puuid, match_info)
    row = participant_info['playerSubteamId']
    col = participant_info['participantId']-1
    if make_sure_participant_info_is_real(participant_info):
        make_damage_graphs(axs, row, col, participant_info)

plt.tight_layout()
plt.show()

