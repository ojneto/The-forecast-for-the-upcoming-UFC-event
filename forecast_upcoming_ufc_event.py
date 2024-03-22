#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import requests
from bs4 import BeautifulSoup
import os.path
from tqdm import tqdm
from datetime import datetime
from joblib import load


# In[2]:


# retorna um objeto Beautiful Soup a partir de uma url
def create_soup(url):
    result = requests.get(url)
    src = result.content
    soup = BeautifulSoup(src,"html.parser")
    return soup
        
def figther_details(corner, url):
    soup = create_soup(url)
    fighter_name = soup.find(class_="b-content__title-highlight").get_text().strip()
    fighter_record = soup.find(class_="b-content__title-record").get_text().strip()
    fighter_record=fighter_record.split(':')[1].strip().split('-')
    fighter_details = soup.find_all('li', class_="b-list__box-list-item b-list__box-list-item_type_block")

    # obtendo os detalhes dos lutadores
    height = fighter_details[0].get_text().strip().split()
    if len(height)==1 or height[1]=='--':
        height = None
    else:
        height = int(height[1][0])*30.48 + int(height[2][0])*2.54
    weight = fighter_details[1].get_text().strip().split()
    if len(weight)==1 or weight[1]=='--':
        weight = None
    else:
        weight = int(weight[1])*0.453592
    reach = fighter_details[2].get_text().strip().split()
    if len(reach)==1 or reach[1]=='--':
        reach = None
    else:
        reach = int(reach[1][0]+reach[1][1])*2.54
    stance = fighter_details[3].get_text().strip().split()
    if len(stance)==1 or stance[1]=='--':
        stance = None
    else:
        stance = stance[1]
    dob = fighter_details[4].get_text().strip().split()
    if len(dob)==1 or dob[1]=='--':
        dob = None
    else:
        dob = dob[1] + ', ' + dob[2] +' '+  dob[3]
    
    # obtendo as estatistica da carreira do lutador
    slpm = fighter_details[5].get_text().strip().split()
    stracc = fighter_details[6].get_text().strip().split()
    sapm = fighter_details[7].get_text().strip().split()
    strdef = fighter_details[8].get_text().strip().split()
    tdavg = fighter_details[10].get_text().strip().split()
    tdacc = fighter_details[11].get_text().strip().split()
    tddef = fighter_details[12].get_text().strip().split()
    subavg = fighter_details[13].get_text().strip().split()

    # criando o dataframe
    dict = {corner + " " + 'Fighter'          : fighter_name,
            corner + " " + 'T Win'            : fighter_record[0],
            corner + " " + 'T Loose'          : fighter_record[1],           
            corner + " " + 'Height (cm)'      : height, 
            corner + " " + 'Weight (kg)'      : weight, 
            corner + " " + 'Reach (cm)'       : reach, 
            corner + " " + 'STANCE'           : stance,
            corner + " " + 'DOB'              : dob,
            corner + " " + 'SLpM'             : float(slpm[1]),
            corner + " " + 'Str. Acc.'    : float(stracc[2].replace('%', ""))/100,
            corner + " " + 'SApM'             : sapm[1],
            corner + " " + 'Str. Def.'    : float(strdef[2].replace('%', ""))/100,
            corner + " " + 'TD Avg.'          : tdavg[2],
            corner + " " + 'TD Acc.'      : float(tdacc[2].replace('%', ""))/100,
            corner + " " + 'TD Def.'      : float(tddef[2].replace('%', ""))/100,
            corner + " " + 'Sub. Avg.'        : subavg[2]
            }

    df = pd.DataFrame(dict, index=[0])

    return df

# retorna um data frame com os detalhes da luta e de cada lutador
def fight_details(url):
    soup = create_soup(url)
    # captura o nome do evento
    event_name = soup.find('h2', class_="b-content__title").get_text().strip()
    
    # Obtendo a classe de peso da luta
    weight_class = soup.find("i", class_='b-fight-details__fight-title').get_text().strip()
    
    # Criando o dataframe
    dict = {'Event'           : event_name,
            'Weight Class'    : weight_class,
            }
    df = pd.DataFrame(dict, index=[0])
    
    # cria uma lista com links contendo os detalhes dos lutadores
    links_fighters = soup.find_all('a', class_="b-link b-fight-details__person-link")
    list1=[]
    for link in links_fighters:
        list1.append(link.get('href'))
    
    # cria um dataframe com os detalhes do lutador do corner vermelho
    df_red = figther_details('Red', list1[0])
    # cria um dataframe com os detalhes do lutador do corner vermelho
    df_blue = figther_details('Blue',list1[1])
       
    return df.join(df_red).join(df_blue)

# retorna uma lista com os links de cada luta de um card
def card_fights(soup):
    table_fights = soup.find_all('tr', class_="b-fight-details__table-row b-fight-details__table-row__hover js-fight-details-click")
    event_fights = []
    for row in table_fights:
        link = row.get('data-link')
        event_fights.append(link)
    return event_fights

# retorna a data de um card
def date(soup):
    soup_date = soup.find_all('li', class_="b-list__box-list-item")
    list_date = soup_date[0].get_text().strip().split()
    date = list_date[1] + " " + list_date[2] + " " + list_date[3]
    # cria o dataframe
        
    df = pd.DataFrame({'Date' : date}, index=[0])
    return df

# retorna um dataframe com as estatisticas de todas as lutas de um card
def card_data(url):
    soup = create_soup(url)
    df_date = date(soup)
    urls = card_fights(soup)
    
    # criando o dataframe
    df = pd.DataFrame()
    for url in tqdm(urls):
        df_fight = fight_details(url)
        df = pd.concat([df, df_date.join(df_fight)], ignore_index=True)
    return df

# retorna o link do card que será feita a previsão
def next_event():
    soup = create_soup('http://ufcstats.com/statistics/events/upcoming')
    links = soup.find_all('a', class_="b-link b-link_style_black")
    l=[]
    for link in links:
        l.append(link.get('href'))
    return l[0]


# In[3]:


# função que transforma os dados em datetime, auxiliar para função cria_variavel_idade
def transforma_data(data):
    data = data.dropna(subset=['Date', 'Red DOB', 'Blue DOB'])
    data['Date'] = data['Date'].apply(lambda x: datetime.strptime(x, '%B %d, %Y').date())
    data['Blue DOB'] = data['Blue DOB'].apply(lambda x: datetime.strptime(x, '%b, %d, %Y').date())
    data['Red DOB'] = data['Red DOB'].apply(lambda x: datetime.strptime(x, '%b, %d, %Y').date())
    return data

#Cria as variáveis de idade para cada lutador
def cria_variavel_idade(data):
    data = transforma_data(data)
    data['Red Age'] = (data['Date'] - data['Red DOB']).apply(lambda x: int(x.days / 365))
    data['Blue Age'] = (data['Date'] - data['Blue DOB']).apply(lambda x: int(x.days / 365))
    return data


# In[6]:


def next_card_prediction():
    # obter os dados do card
    print("Loading the data and the model:")
    # Carregar o modelo salvo
    model = load('modelo_regressao_logistica.joblib')
    df = card_data(next_event())
    # crias as variaveis idades
    df = cria_variavel_idade(df)
    print('Data and model loaded successfully. \n')
    print('Event: ' + df.loc[0,'Event'])
    print("Date: " + str(df.loc[0,'Date']) + "\n")
    # variaves preditoras
    X_variables = ['Red T Win', 'Red T Loose', 'Red Height (cm)',
                   'Red Weight (kg)', 'Red Reach (cm)', 'Red Age',
                   'Blue T Win', 'Blue T Loose', 'Blue Height (cm)', 'Blue Weight (kg)',
                   'Blue Reach (cm)', 'Blue Age', 'Red SLpM',
                   'Red Str. Acc.', 'Red SApM', 'Red Str. Def.', 'Red TD Avg.',
                   'Red TD Acc.', 'Red TD Def.', 'Red Sub. Avg.', 'Blue SLpM',
                   'Blue Str. Acc.', 'Blue SApM', 'Blue Str. Def.', 'Blue TD Avg.',
                   'Blue TD Acc.', 'Blue TD Def.', 'Blue Sub. Avg.']
    X_pred = df[X_variables]
    preds = model.predict_proba(X_pred)
    df_preds = df.loc[X_pred.index, ['Red Fighter', 'Blue Fighter']]
    # Adiciona duas colunas ao DataFrame limpo com os dados do array
    df_preds['Red Odds'] = preds[:, 0]
    df_preds['Red Odds'] = preds[:, 0]
    df_preds['Blue Odds'] = preds[:, 1]  
    df_preds = df_preds[['Red Fighter', 'Red Odds', 'Blue Odds', 'Blue Fighter']]
    df_preds.to_csv(str(df.loc[0,'Date']) + '.csv', index = False)
    print(df_preds)
    print('\n The predictions were saved in the file ' + str(df.loc[0,'Date']) + '.csv')


# In[7]:


next_card_prediction()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




