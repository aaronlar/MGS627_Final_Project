#importing the required packages and libraries to run the code
import requests
import pandas as pd
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
#this is all the information that needs to be provided so the player can be identified and the
#api requests won't be denied
#Riot API Key
api_key = 'your api key here'
#Name in League of Legends
gameName = 'Volani'
#region of player
region = 'NA1'
#the tagline of the player
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
champDataUrl = 'https://ddragon.leagueoflegends.com/cdn/14.23.1/data/en_US/champion.json'
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
    #checking that I have a name for every champ in the game as of the latest patch for the game there is 169
    #as of 12/2/2024
    if len(champNames) == 169:
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

def get_recent_match_history(puuid):
    """
    This function sends an api request to the matches API for league of legends to retrieve recent matches in the form
    of a list. It returns the last 20 games played by the player whose puuid is passed in a list.
    :param puuid: this the puuid of the player that is entered at the top of the file
    :return: this returns a list of match ID's of the last 20 games played by
    the player whose information is entered at the top of the file
    """
    #grabbing the last 20 matches matchID to get more information from them
    matchURL = 'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/'+puuid+'/ids?start=0&count=20&'
    #making the request
    matchResponse = requests.get(matchURL, headers=headers)
    #error handling with function
    errorHandlingForRequests(matchResponse)
    #parsing the JSON
    matches = matchResponse.json()
    #returning the list of match ID's
    return matches
#calling the function
recent_match_history = get_recent_match_history(puuid)
#making a function to extract the data about a match using the match ID
def get_match_info(matchID):
    """
    this function sends an api request to the matches API for league of legends to retrieve the information about 1
    match specified by the match id provided.
    :param matchID: this is a match id from the list made in the get_recent_match_history function
    :return: It returns a large dictionary that is the information about 1 match
    """
    #assembling the url
    matchInfoUrl ='https://americas.api.riotgames.com/lol/match/v5/matches/'+matchID
    #making the request
    matchInfoResponse = requests.get(matchInfoUrl, headers=headers)
    #error handling with function
    errorHandlingForRequests(matchInfoResponse)
    #parsing the JSON
    matchInfo = matchInfoResponse.json()
    #returning the dictionary
    return matchInfo
#calling the function
match_info = get_match_info(recent_match_history[0])

def get_player_info_from_puuid(puuid, match_info):
    """
    this function extracts the information of 1 player from the entire information of 1 match and returns it in the form
    of a dictionary
    :param puuid: a puuid of a player in the match
    :param match_info: the information of 1 match as defined in the get_match_info function
    :return: a dictionary that only contains the information specific to the player with the puuid specified from the
    match specified
    """
    #establish participant info as a variable
    participant_info = None
    #making a loop in order to loop over the match info participants
    for participant in match_info['info']['participants']:
        #checking that the puuid of the participant is the same as the puuid passed into the function
        if participant['puuid'] == puuid:
            #making the participant into the participant info to return
            participant_info = participant
    #return the dictionary of participant info
    return participant_info
#calling the function
participant_info = get_player_info_from_puuid(puuid, match_info)
def make_sure_participant_info_is_real(participant_info):
    """
    this function is error checking to make sure that the participant info is really a real player
    :param participant_info: a dictionary containing information from a single player in a match
    :return: nothing
    """
    #checking that there is something in participant info
    if participant_info is None:
        #if there is nothing in participant info prints a message to let you know
        print('participant does not exist')
#calling the function
make_sure_participant_info_is_real(participant_info)

def make_damage_graph(participant_info):
    """
    this function makes a graph for the damage taken by a single player in a match
    :param participant_info: all the info from 1 player in the match
    :return: a graph that contains a bar with all the damage taken by a single player in a game
    """
    #making the figure and axes in a subplot because it was what I remembered
    fig, ax = plt.subplots()
    #makes the physical damage part of the bar
    ax.bar(participant_info['championName'], participant_info["physicalDamageTaken"],
        label='Physical Damage Taken ' + str(participant_info['physicalDamageTaken']), color='orange')
    #makes the magic damage part of the bar on top of the physical damage bar
    ax.bar(participant_info['championName'], participant_info["magicDamageTaken"],
        bottom=participant_info["physicalDamageTaken"],
        label='Magic Damage Taken ' + str(participant_info['magicDamageTaken']), color='b')
    #makes the true damage part of the bar on top of the mage and physical damage bars
    ax.bar(participant_info['championName'], participant_info['trueDamageTaken'],
        bottom=participant_info['physicalDamageTaken'] + participant_info['magicDamageTaken'],
        label='True Damage Taken ' + str(participant_info['trueDamageTaken']), color='silver')
    #add a legend to the plot
    ax.legend()
    #add a title to the plot
    plt.title(gameName + ' Damage Taken')
    #showing the plot
    plt.show()

def make_damage_graphs(ax, row, col, participant_info):
    """
    the matplotlib code to populate a large plot with the subplots about the damage taken by a single player
    :param ax: the axis you want to add the bar to
    :param row: the row in the larger plot
    :param col: the column in the larger plot
    :param participant_info: the information of the player the graph is about
    :return:
    """
    #makes the physical damage part of the bar
    ax[row, col].bar(participant_info['championName'], participant_info["physicalDamageTaken"],
           label='Physical Damage Taken ' + str(participant_info['physicalDamageTaken']), color='orange')
    #makes the magic damage part of the bar on top of the physical damage part
    ax[row, col].bar(participant_info['championName'], participant_info["magicDamageTaken"],
           bottom=participant_info["physicalDamageTaken"],
           label='Magic Damage Taken ' + str(participant_info['magicDamageTaken']), color='b')
    #makes the true damage part of the bar on top of the magic and phyical damage parts
    ax[row, col].bar(participant_info['championName'], participant_info['trueDamageTaken'],
           bottom=participant_info['physicalDamageTaken'] + participant_info['magicDamageTaken'],
           label='True Damage Taken ' + str(participant_info['trueDamageTaken']), color='silver')
    #add a legend
    ax.legend()
    #add a title
    ax.set_title(participant_info['championName'] + ' Damage Taken')

#makes an empty list to put the puuids in the match into
puuids = []
#loop over the puuids in the match info
for participant in match_info['info']['participants']:
    #put the puuid in the list
    puuids.append(participant['puuid'])


def make_damage_taken_graphs_plotly(fig, row, col, participant_info):
    """
    the plotly code to moke a bar graph of the damage taken by a single player and the damage types
    :param fig: the plotly figure
    :param row: the row in the larger plot
    :param col: the column in the larger plot
    :param participant_info: the information of the player the graph is about
    :return: the plotly graph for a single player
    """
    #add the physical damage part of the bar
    fig.add_trace(
        go.Bar(
            x=[participant_info['championName']],
            y=[participant_info['physicalDamageTaken']],
            name='Physical Damage Taken ' + str(participant_info['physicalDamageTaken']),
            marker_color='orange'),
        row=row, col=col)
    #add the magic damage part of the bar on top of the physical part
    fig.add_trace(
        go.Bar(
            x=[participant_info['championName']],
            y=[participant_info['magicDamageTaken']],
            name='Magic Damage Taken ' + str(participant_info['magicDamageTaken']),
            marker_color='blue',
            base=participant_info['physicalDamageTaken']),
        row=row, col=col)
    #add the true damage part of the bar on top of the magic and phyiscal parts
    fig.add_trace(
        go.Bar(
            x=[participant_info['championName']],
            y=[participant_info['trueDamageTaken']],
            name='True Damage Taken ' + str(participant_info['trueDamageTaken']),
            marker_color='silver',
            base=participant_info['physicalDamageTaken'] + participant_info['magicDamageTaken']),
        row=row, col=col)
    #make the bars stacked and not have a legend
    fig.update_layout(barmode='stack', showlegend=False)

def make_damage_dealt_graphs_plotly(fig, row, col, participant_info):
    """
    the plotly code to make a bar graph of the damage dealt by a single player and the damage types
    :param fig: the plotly figure
    :param row: the row in the larger plot
    :param col: the column in the larger plot
    :param participant_info: the information of the player the graph is about
    :return: the plotly graph for a single player
    """
    #makes the physical damage bar
    fig.add_trace(
        go.Bar(
            x=[participant_info['championName']],
            y=[participant_info['physicalDamageDealt']],
            name='Physical Damage Dealt ' + str(participant_info['physicalDamageDealt']),
            marker_color='orange'
        ),
        row=row, col=col)
    #makes the magic damage part of the bar on top of the physical part
    fig.add_trace(
        go.Bar(
            x=[participant_info['championName']],
            y=[participant_info['magicDamageDealt']],
            name='Magic Damage Dealt ' + str(participant_info['magicDamageDealt']),
            marker_color='blue',
            base=participant_info['physicalDamageDealt']),
        row=row, col=col)
    #make the true damamge part of the bar on top of the other parts
    fig.add_trace(
        go.Bar(
            x=[participant_info['championName']],
            y=[participant_info['trueDamageDealt']],
            name='True Damage Dealt ' + str(participant_info['trueDamageDealt']),
            marker_color='silver',
            base=participant_info['physicalDamageDealt'] + participant_info['magicDamageDealt']),
        row=row, col=col)
    #make the bars stack and don't show the legend
    fig.update_layout(barmode='stack', showlegend=False)

def make_damage_dealt_champions_graphs_plotly(fig, row, col, participant_info):
    """
    the plotly code to make a bar graph of the damage dealt by a single player to champions and the damage types
    :param fig: the plotly figure
    :param row: the row in the larger plot
    :param col: the column in the larger plot
    :param participant_info: the information of the player the graph is about
    :return: the plotly graph for a single player
    """
    #make the physical damage bar
    fig.add_trace(
        go.Bar(
            x=[participant_info['championName']],
            y=[participant_info['physicalDamageDealtToChampions']],
            name='Physical Damage Dealt To Champions ' + str(participant_info['physicalDamageDealtToChampions']),
            marker_color='orange'),
        row=row, col=col)
    #make the magic damage bar on top of the physical one
    fig.add_trace(
        go.Bar(
            x=[participant_info['championName']],
            y=[participant_info['magicDamageDealtToChampions']],
            name='Magic Damage Dealt To Champions ' + str(participant_info['magicDamageDealtToChampions']),
            marker_color='blue',
            base=participant_info['physicalDamageDealtToChampions']),
        row=row, col=col)
    #make the true damage bar on top of the other 2
    fig.add_trace(
        go.Bar(
            x=[participant_info['championName']],
            y=[participant_info['trueDamageDealtToChampions']],
            name='True Damage Dealt To Champions ' + str(participant_info['trueDamageDealtToChampions']),
            marker_color='silver',
            base=participant_info['physicalDamageDealtToChampions'] + participant_info['magicDamageDealtToChampions']),
        row=row, col=col)
    #stack the bars and don't show the legend
    fig.update_layout(barmode='stack', showlegend=False)

#this is where the Dash app begins
# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div(
    #black background and center aligned text
    style={'backgroundColor': 'black', 'textAlign': 'center'},
    children=[
        #title in white text
        html.H1(
            children='League of Legends Match Data',
            style={'color': 'white'}
        ),
        #a dropdown with the match id's from recent match history to pick from, base value is the first match id in the list
        dcc.Dropdown(
            id='dropdown',
            options=[{'label': match_id, 'value': match_id} for match_id in recent_match_history],
            value=recent_match_history[0],
            style={'width': '50%', 'margin': 'auto'}
        ),
        #the damage taken graph
        dcc.Graph(id='damage-taken-graph'),
        #the damage dealt graph
        dcc.Graph(id='damage-dealt-graph'),
        #the damage dealt to champions graph
        dcc.Graph(id='damage-dealt-champions-graph')
    ]
)


#the callback to update the graphs based on dropdown selection
@app.callback(
    [Output('damage-taken-graph', 'figure'),
     Output('damage-dealt-graph', 'figure'),
     Output('damage-dealt-champions-graph', 'figure')],
    [Input('dropdown', 'value')]
)
#function to update the graphs when the dropdown selection is changed
def update_graphs(selected_match):
    match_info = get_match_info(selected_match)
    puuids = []
    # loop over the puuids in the match info
    for participant in match_info['info']['participants']:
        # put the puuid in the list
        puuids.append(participant['puuid'])

    # Update the Damage Taken Graph
    damage_taken_fig = make_subplots(rows=2, cols=5, shared_yaxes=True)
    make_damage_taken_graphs_plotly(damage_taken_fig, 1, 1, get_player_info_from_puuid(puuids[0], match_info))
    make_damage_taken_graphs_plotly(damage_taken_fig, 1, 2, get_player_info_from_puuid(puuids[1], match_info))
    make_damage_taken_graphs_plotly(damage_taken_fig, 1, 3, get_player_info_from_puuid(puuids[2], match_info))
    make_damage_taken_graphs_plotly(damage_taken_fig, 1, 4, get_player_info_from_puuid(puuids[3], match_info))
    make_damage_taken_graphs_plotly(damage_taken_fig, 1, 5, get_player_info_from_puuid(puuids[4], match_info))
    make_damage_taken_graphs_plotly(damage_taken_fig, 2, 1, get_player_info_from_puuid(puuids[5], match_info))
    make_damage_taken_graphs_plotly(damage_taken_fig, 2, 2, get_player_info_from_puuid(puuids[6], match_info))
    make_damage_taken_graphs_plotly(damage_taken_fig, 2, 3, get_player_info_from_puuid(puuids[7], match_info))
    make_damage_taken_graphs_plotly(damage_taken_fig, 2, 4, get_player_info_from_puuid(puuids[8], match_info))
    make_damage_taken_graphs_plotly(damage_taken_fig, 2, 5, get_player_info_from_puuid(puuids[9], match_info))
    #add a title to the graph
    damage_taken_fig.update_layout(title=f'Damage Taken for Every Champion in MatchID {selected_match}')

    #Update the Damage Dealt Graph
    damage_dealt_fig = make_subplots(rows=2, cols=5, shared_yaxes=True)
    make_damage_dealt_graphs_plotly(damage_dealt_fig, 1, 1, get_player_info_from_puuid(puuids[0], match_info))
    make_damage_dealt_graphs_plotly(damage_dealt_fig, 1, 2, get_player_info_from_puuid(puuids[1], match_info))
    make_damage_dealt_graphs_plotly(damage_dealt_fig, 1, 3, get_player_info_from_puuid(puuids[2], match_info))
    make_damage_dealt_graphs_plotly(damage_dealt_fig, 1, 4, get_player_info_from_puuid(puuids[3], match_info))
    make_damage_dealt_graphs_plotly(damage_dealt_fig, 1, 5, get_player_info_from_puuid(puuids[4], match_info))
    make_damage_dealt_graphs_plotly(damage_dealt_fig, 2, 1, get_player_info_from_puuid(puuids[5], match_info))
    make_damage_dealt_graphs_plotly(damage_dealt_fig, 2, 2, get_player_info_from_puuid(puuids[6], match_info))
    make_damage_dealt_graphs_plotly(damage_dealt_fig, 2, 3, get_player_info_from_puuid(puuids[7], match_info))
    make_damage_dealt_graphs_plotly(damage_dealt_fig, 2, 4, get_player_info_from_puuid(puuids[8], match_info))
    make_damage_dealt_graphs_plotly(damage_dealt_fig, 2, 5, get_player_info_from_puuid(puuids[9], match_info))
    #add a title to the grpah
    damage_dealt_fig.update_layout(title=f'Damage Dealt by Every Champion in MatchID {selected_match}')

    #Update the Damage Dealt to Champions Graph
    damage_dealt_champions_fig = make_subplots(rows=2, cols=5, shared_yaxes=True)
    make_damage_dealt_champions_graphs_plotly(damage_dealt_champions_fig, 1, 1, get_player_info_from_puuid(puuids[0], match_info))
    make_damage_dealt_champions_graphs_plotly(damage_dealt_champions_fig, 1, 2, get_player_info_from_puuid(puuids[1], match_info))
    make_damage_dealt_champions_graphs_plotly(damage_dealt_champions_fig, 1, 3, get_player_info_from_puuid(puuids[2], match_info))
    make_damage_dealt_champions_graphs_plotly(damage_dealt_champions_fig, 1, 4, get_player_info_from_puuid(puuids[3], match_info))
    make_damage_dealt_champions_graphs_plotly(damage_dealt_champions_fig, 1, 5, get_player_info_from_puuid(puuids[4], match_info))
    make_damage_dealt_champions_graphs_plotly(damage_dealt_champions_fig, 2, 1, get_player_info_from_puuid(puuids[5], match_info))
    make_damage_dealt_champions_graphs_plotly(damage_dealt_champions_fig, 2, 2, get_player_info_from_puuid(puuids[6], match_info))
    make_damage_dealt_champions_graphs_plotly(damage_dealt_champions_fig, 2, 3, get_player_info_from_puuid(puuids[7], match_info))
    make_damage_dealt_champions_graphs_plotly(damage_dealt_champions_fig, 2, 4, get_player_info_from_puuid(puuids[8], match_info))
    make_damage_dealt_champions_graphs_plotly(damage_dealt_champions_fig, 2, 5, get_player_info_from_puuid(puuids[9], match_info))
    #add a title to the graph
    damage_dealt_champions_fig.update_layout(title=f'Damage Dealt to Champions by Every Champion in MatchID {selected_match}')
    #return the updated graphs
    return damage_taken_fig, damage_dealt_fig, damage_dealt_champions_fig


# Run the app, hopefully
if __name__ == '__main__':
    app.run_server(debug=False)