# -*- coding: utf-8 -*-
import streamlit as st 
from bs4 import BeautifulSoup
import  requests
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common import keys
from bs4 import BeautifulSoup
import  requests
import os
from selenium.common.exceptions import ElementNotInteractableException
import time

@st.cache
def get_stats(player, lg):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path= 'D:/Chrome Downloads/chromedriver_win32/chromedriver.exe', options = chrome_options)
    driver.get('https://fbref.com')
    driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[3]/form/div/div/input[2]')\
        .send_keys(player)
    time.sleep(2)
    try:
        driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[3]/form/div/div/div/div[1]/div[2]/div/div').click()
        url = driver.current_url
        split = url.rsplit('/',1)
        time.sleep(1.5)
        url = split[0]+'/matchlogs/2019-2020/summary/'+split[1]+'-match-logs'
        driver.get(url)
        time.sleep(2)
    except NoSuchElementException:
        print('Element not found in dropdown...Searching By pressing search button directly')
        driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[3]/form/input[1]').click()
        url = driver.current_url
        split = url.rsplit('/',1)
        time.sleep(1.5)
        url = split[0]+'/matchlogs/2019-2020/summary/'+split[1]+'-match-logs'
        driver.get(url)
        time.sleep(2)
    except :
        print('Cannot locate player... Searching next player')    
        return -1
    
    soup = BeautifulSoup(driver.page_source)
    
    #Putting stats in  a list
    try:
        stats = soup.find('table',{'class':'min_width'}).find('tbody').find_all('tr')
    except:
        print('Nai chalega')
        return

    for count, i in enumerate(stats):
        if i.has_attr('class'):
            stats.pop(count)  

    try:            
        for count, i in enumerate(stats):
            if i.find('td', {'data-stat' : 'comp'}).find('a').text != lg :
                stats.pop(count)
    except:
        stats.pop(count)

    stats = stats[-6:]
    new_row = list()
    for row in stats:
        ind_row = list()
        for j in row.find_all('td'):
            ind_row.append(j.text)
        new_row.append(ind_row)

    #Calculation of mean for prediction
    cols = ['Day','Comp','Round','Venue','Result','Squad','Opponent','Start','Pos','Min'
            ,'Gls','Ast','PK','PKatt','Sh','SoT','CrdY','CrdR','Touches','Press','Tkl','Int','Blocks',
            'xG','npxG','xA','SCA','GCA','Cmp','PAtt','Cmp%','PrgDist','Carries','CPrgDist','Succ',
            'Att','Match Report']

    try:
        data = pd.DataFrame(new_row, columns = cols)
        data = data[data['Comp'] == lg]

    except ValueError as e:
        return
    final_data = data[['Comp','Min','Gls','Ast','PK','PKatt','Sh','SoT','CrdY','CrdR','Touches','Press','Tkl','Int','Blocks',
            'xG','npxG','xA','SCA','GCA','Cmp','PAtt','Cmp%','PrgDist','Carries','CPrgDist','Succ',
            'Att']]
    return final_data



def get_league(link):
    global soup
    league = requests.get(link)
    soup = BeautifulSoup(league.text, features= 'html.parser')
    return soup


def stats_mean_goals(df):
    pred_data = df.loc[:,['Min','Ast','Sh','SoT','npxG','xA','SCA','GCA','Succ']] 
    pred_data.dropna(how='all', inplace = True)
    mode_goals = pred_data['Min'].mode()
    mode_goals = pd.Series(mode_goals.max())
    mean_goals = pred_data.iloc[:,1:].mean()
    final_goals = [mode_goals, mean_goals]
    goal_stats = pd.concat(final_goals, axis = 0).values
    # mean_stats = df.mode().values.reshape(1,-1)
    return goal_stats



st.title('Welcome to Reality 11')
leagues = ['Select','Premier League','Serie A','La Liga', 'Bundesliga', 'Ligue 1' ]
league = st.selectbox('Select league', leagues)

if league == 'Premier League':
    soup = get_league('https://www.rotowire.com/soccer/lineups.php')
    st.write('Link captured Successfully')

if league == 'Serie A':
    soup = get_league('https://www.rotowire.com/soccer/lineups.php?league=SERI')
    st.write('Link captured Successfully')

if league == 'La Liga':
    soup = get_league('https://www.rotowire.com/soccer/lineups.php?league=LIGA')
    st.write('Link captured Successfully')

if league == 'Bundesliga':
    soup = get_league('https://www.rotowire.com/soccer/lineups.php?league=BUND')
    st.write('Link captured Successfully')

if league == 'Ligue 1':
    soup = get_league('https://www.rotowire.com/soccer/lineups.php?league=FRAN')
    st.write('Link captured Successfully')
st.write('Selected League: ', league)


# select = st.selectbox('Get Lineup',['Get Lineups'])
# if select == 'Get Lineups':

card = st.number_input('Enter Card No:',min_value = 0, value = -1, step = 1)
if card == -1:
    st.write('Select the Lineup number from WWW.ROTOWIRE.COM')
else:
    st.write('Selected:', card)
    lineups = soup.find('div',class_="lineups").find_all('div',class_="lineup is-soccer")
    match = lineups[card].find('div', {'class':"lineup__box"}).find('div',{'class':"lineup__main"}).find_all('ul')
    squad = dict()
    for r in range(0,2):
        lp = match[r].find_all('li')
        squad.update({lp[i].find('a')['title']:['Home' if r == 0 else 'Away'\
                                                ,lp[i].find('div').text] for \
                    i in range(7,12)})
    if st.checkbox('Show Lineup'):
        st.write(squad.keys())


# get_players = st.selectbox('Get Players',['Select','Get players'])
# if get_players == 'Get players':
if st.checkbox('Get Player stats'):
    player_dict = dict()
    for footballer in squad:
        st.write('Getting: ',footballer)
        mean = get_stats(footballer, league)
        try:
            if (mean.empty):
                st.write('Failed to retrive stats')
            else:
                player_dict[footballer] = mean
                st.write('Successfully Written:',footballer)
        except:
            st.write('Sorry! Stats not found')
            

if st.checkbox('Show captured values'):
    captured_stats = dict()
    for player in player_dict.keys():
        try:
            p = player_dict[player].iloc[:,1:].astype('float64')
            captured_stats[player] = p
            st.dataframe(captured_stats.keys())  
            st.dataframe(captured_stats[player])   
        except AttributeError as e  :
            print(e)
            continue


# if st.checkbox('Show captured values'):
#     for player in player_dict.keys():
#         try:
#             st.dataframe(player_dict.keys())  
#             st.dataframe(player_dict[player])   
#         except AttributeError as e  :
#             print(e)
#             continue


 

prediction_types = ['Select','Passing','Goals','Assists']
prediction_type = st.selectbox('Select Type of Prediction', prediction_types)

# #For Passing
# if st.button('Predict', key = 0 ) and prediction_type == 'Passing':
#     import joblib
#     model = joblib.load('passing_model.sav')
#     # prediction_data = captured_stats.loc[:,['Sh','Touches','Tkl','SCA','GCA','Att','Carries','PrgDist']].mean().values
#     for plyr in captured_stats.keys():
#         prediction_data = captured_stats[plyr].loc[:,['Sh','Touches','Tkl','SCA','GCA','Att','Carries','PrgDist']].mean().values.reshape(1,-1)
#         st.write('Prediction Data:',prediction_data)
#         # try:
#         pred = model.predict(prediction_data)
#         # except ValueError:
#         #     st.write('File not found')
#         #     continue
#         st.write('Predicted passes for: ',plyr)
#         st.write(pred[0])



#For Goals
if st.button('Predict',key = 1) and prediction_type == 'Goals':
    import joblib
    model = joblib.load('goal_model.sav')
    for plyr in player_dict.keys():
        threshold_goals = .35
        prediction_data = stats_mean_goals(captured_stats[plyr])
        # try:
        pred = model.predict_proba([prediction_data])
        # except ValueError:
        #     st.write('File not found')
        #     continue
        st.write('Probablity of Scoring: ',plyr)
        st.write(round(pred[0][1],2)*100,'%')


# #For Assists
# if st.button('Predict',key = 2) and prediction_type == 'Passing':
#     import joblib
#     model = joblib.load('passing_model.sav')
#     prediction_data = captured_stats.loc[:,['Sh','Touches','Tkl','SCA','GCA','Att','Carries','PrgDist']].mean().values
#     for plyr in player_dict.keys():
#         # try:
#         pred = model.predict([prediction_data])
#         # except ValueError:
#         #     st.write('File not found')
#         #     continue
#         st.write('Predicted passes for: ',plyr)
#         st.write(int(pred[0]))
            
            
            
            
            
            
        