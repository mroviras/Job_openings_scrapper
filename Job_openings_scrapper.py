###############################################################################
# DATE: 20/12/2022

# AUTHOR: Marti Rovira

# AIM: Get a random sample of job openings from the API reed dot
# co dot uk from specific locations and using specific concepts for search. The code 
# allows to exclude jobs depending from a variety of criteria, such as not applying
# twice to the same company or branch, or above a specific salary. The code also allows
# to insert empty or pre-filled columns in the final file. The final form was useful
# in conducting a field experiment.

# REQUIREMENTS: Excel file entitled offers_previously_applied.xlsx with columns Jobid 
# (id from the job opening), employerName (name of the company), location_original (
# location from which the job has been searched) and a column called ('Reapply?'). This 
# last column should be filled manually with a 'Yes' if he wants that the code choose other
# jobs from the company/branch (e.g. because the job opening selected is not 
# suitable from the needs of the researcg) or 'No' if no other job from the company/branch should be
# chosen. A sample of the file can be seen in the Github page also containing this code.

# There is also need of a file entitled api_reed_password.txt in the Working Directory 
# including the password for the reed dot co dot uk API.

# OUTPUTS: CSV file with all emails downloaded (CRUK_job_offers_population.csv) and 
# a file with the jobs to apply to (applications + date.csv).

# NOTE1: This is one the first code code I share publicly. Please, feel free to reach me
# to suggest any improvements.

###############################################################################

##############################################################################
# Parameters that can be easily changed by the user.
##############################################################################

## Number of job openings selected at the end.

cruk_numberofferstoday = 30 

## Maximum salary beyond no jobs will be chosen

cruk_maxsalary = 30000 

## Locations from which jobs should be searched

cruk_locations=[
    'Southampton',
    'Oxford',
    'Cardiff'
]

## Concepts for searching jobs
# The first concept for each block (e.g. 'Catering' or 'Barista') will 
# be used to characterize the rest of the elements of the block.

cruk_concepts=[
   ['"Catering"',
        '"Restaurant"',
        '"Barista"'],
    ['"Construction"',
        '"Labourer"',
        '"Groundworker"',
    ]
]


##############################################################################
# Setting parameters
##############################################################################

## libraries

import numpy as np
import pandas as pd
#from pandas import * 

import requests
import json
from getpass import getpass
from os import path
from time import sleep
import random
import os
import glob
import datetime
import shutil

# Defining anti_join programme
def anti_join(x, y, on):
    """Return rows in x which are not present in y"""
    ans = pd.merge(left=x, right=y, how='left', indicator=True, on=on)
    ans = ans.loc[ans._merge == 'left_only', :].drop(columns='_merge')
    return ans

   # Source: https://gist.github.com/sainathadapa/eb3303975196d15c73bac5b92d8a210f
    
# Setting paths 

path0 = os.getcwd()

# Setting passwords

api_reed_access = open(path0 + '/api_reed_password.txt', 'r')
api_reed_code = api_reed_access.read()
api_reed_access.close() 

# Setting date and time

today = datetime.date.today()
datetoday = today.strftime("%d/%m/%Y")
datetoday2 = today.strftime("%Y_%m_%d")

now=datetime.datetime.now()
time = now.strftime("%H:%M:%S")
time2 = now.strftime("%H_%M_%S")

# Timeout time

timeouttimevalue = 120

##############################################################################
# Inserting today CRUK job offers into the general population database
##############################################################################



################ Downloading data

# Creating a folder titled 'jobs_today' that will be used to store information
os.makedirs('jobs_today', mode = 0o777, exist_ok = True)
path = path0 + '/jobs_today/'

##### Creating one database per place and concept

errors_count=0

for location in cruk_locations:
    for concept in cruk_concepts:
        try:
            concept0=concept[0].replace('"', '')
            concept_str = ', '.join(concept)

            namefile = path + datetoday2 + "_" + location + "_" + concept0 + ".csv"

            if os.path.exists(namefile):
                print (concept0  + " " + location + " " + "ALREADY EXISTS!")

            else:
                url = 'https://www.reed.co.uk/api/1.0/search?' \
                        + 'postedByDirectEmployer=' + 'true' \
                        + '&distanceFromLocation=' + '10'\
                        + '&locationName=' + location  \
                        + '&keywords=' + concept_str 

                JSONContent = requests.get(url, auth=(api_reed_code,""), timeout=timeouttimevalue).json() 
                    # Allows to capture the total number of requests 

                JSONContent_fulldb = [] 
                    # Creates the space on which the json requests will be saved

                for i in range(0, JSONContent['totalResults'], 100): 
                    # Helps to avoid the restriction of providing 100 results per request
                    url = url +'&resultstoSkip='+str(i)
                    JSONContent = requests.get(url, auth=(api_reed_code,""), timeout=timeouttimevalue).json() 
                        # Requesting the information for that round
                    JSONContent_fulldb.append(JSONContent) 
                    # Appending the info to the joined space
                    print(concept0  + " " + location + ": " + str(i) +' out of '+str(JSONContent['totalResults']), end="\r")
                    # Helps to control what is going on
                    sleep(2) 
                    # Waiting one second for avoiding overasking the reed.co.uk API

                content = json.dumps(JSONContent_fulldb, indent = 4, sort_keys=True) 
                # json.dumps encodes the information to Phyton format?


                if JSONContent['totalResults'] % 100 == 0:
                    range_out = (JSONContent['totalResults']/100)

                else:
                    range_out = (JSONContent['totalResults']/100)+1 
                    # This helps in the decoding of the programme


                dataset2 = pd.DataFrame(columns=['Jobid', 
                                                 'employerId',
                                                 'employerName',
                                                 'Job',
                                                 'Location',
                                                 'Date',
                                                 'ExpirationDate',
                                                 'Description',
                                                 'Minsalary',
                                                 'Maxsalary',
                                                 'currency',
                                                 'applications',
                                                 'url'])
                for j in range(0,int(range_out)):
                    location_list = []
                    json1_data = json.loads(content)[j]
                    for var in json1_data['results']:
                        location_list.append([var['jobId'], 
                                            var['employerId'], 
                                            var['employerName'],
                                            var['jobTitle'], 
                                            var['locationName'], 
                                            var['date'], 
                                            var['expirationDate'], 
                                            var['jobDescription'], 
                                            var['minimumSalary'], 
                                            var['maximumSalary'], 
                                            var['currency'], 
                                            var['applications'],
                                            var['jobUrl']])
                    dataset = pd.DataFrame(location_list)
                    dataset.columns = ['Jobid', 
                                       'employerId',
                                       'employerName',
                                       'Job',
                                       'Location',
                                       'Date',
                                       'ExpirationDate',
                                       'Description',
                                       'Minsalary',
                                       'Maxsalary',
                                       'currency',
                                       'applications',
                                       'url']
                    dataset2 = pd.concat([dataset2, dataset], sort=False)

                    concept0=concept[0].replace('"', '')

                    # Identifying the location + concept + date + time
                    dataset2['location_original']=location
                    dataset2['concept_original']=concept0
                    dataset2['first_seen_date']=datetoday
                    dataset2['first_seen_time']=time

                namefile = path + datetoday2 + "_" + location + "_" + concept0 + ".csv"
                dataset2.to_csv(namefile, sep=';')
                print("\r", end="")
                print( concept0  + " " + location + " " + '\U0001F44C' + "               ")
           
        except (requests.exceptions.Timeout) as error :
                print("\r", end="")
                print( concept0  + " " + location + ": " + + str(i) +' out of '+str(JSONContent['totalResults']) + "ERROR. YOU SHOULD RETRY")
                errors_count = errors_count + 1
                
print(datetoday + ": Data collection is finnished. Number of errors:" + str(errors_count))

# Combining all files and creating population database for today job openings

os.chdir(path)
all_filenames = [i for i in glob.glob('*.{}'.format('csv'))]
CRUK_job_offers_today = pd.concat([pd.read_csv(f, sep=';') for f in all_filenames ], sort=False)

namefile = "CRUK_job_offers_population" + datetoday2 + ".csv" 
CRUK_job_offers_today.to_csv( namefile, index=False, encoding='utf-8-sig', sep=';')

index0 = CRUK_job_offers_today.index

#### Joining today list of job openings with a list from previous days

os.chdir(path0)

path_CRUK_jo_pop = path0 + "/CRUK_job_offers_population.csv"
isFile = os.path.isfile(path_CRUK_jo_pop)

if isFile == True:

    CRUK_job_offers_population = pd.read_csv(path_CRUK_jo_pop, sep=';')

    CRUK_job_offers_population = pd.concat([CRUK_job_offers_population, 
                                        CRUK_job_offers_today], sort=False)

    CRUK_job_offers_population=CRUK_job_offers_population.drop_duplicates(
        subset=["Jobid"], 
        keep='last', 
        inplace=False) # Only keep records of the last time job opening is detected

    CRUK_job_offers_population=CRUK_job_offers_population.loc[:, 
        ~CRUK_job_offers_population.columns.str.contains('^Unnamed')]

    index2 = CRUK_job_offers_today.index

    CRUK_job_offers_population.to_csv(path_CRUK_jo_pop, sep=';')

else:
    CRUK_job_offers_today.to_csv(path_CRUK_jo_pop, sep=";")

print(datetoday + ": Final dataset is created!")

##############################################################################
# Selecting applications
##############################################################################

os.chdir(path0)

#### Excluding job openings with a late deadline

path_CRUK_jo_pop = path + "CRUK_job_offers_population" + datetoday2 + ".csv" 
CRUK_job_offers_population= pd.read_csv(path_CRUK_jo_pop, sep=';')

CRUK_job_offers_population['ExpirationDate'] = pd.to_datetime(CRUK_job_offers_population['ExpirationDate'], infer_datetime_format=True)
CRUK_job_offers_population['Date'] = pd.to_datetime(CRUK_job_offers_population['Date'], infer_datetime_format=True)

applications_today = CRUK_job_offers_population[
    CRUK_job_offers_population['ExpirationDate'] >= pd.Timestamp('today')]

#### Excluding job openings by companies + region on which I already applied in the past

offers_previosly_applied_file = path0 + "/offers_previously_applied.xlsx"
applications_prev = pd.read_excel(offers_previosly_applied_file)
applications_prev_filtered = applications_prev[applications_prev["Reapply?"]!="Yes"]

applications_today  = anti_join(applications_today , applications_prev_filtered, ['employerName', 'location_original'])

# Cleaning the dataset 
applications_today =applications_today.loc[
    :, ~applications_today .columns.str.contains('^Unnamed')]
applications_today =applications_today .loc[
    :, ~applications_today.columns.str.contains('_y$')]
applications_today.columns = applications_today.columns.str.rstrip('_x')  

#### Excluding job openings I had already applied in the past

applications_prev = pd.read_excel(offers_previosly_applied_file)

applications_prev["Jobid"] = applications_prev["Jobid"].astype(int)
applications_today["Jobid"] = applications_today["Jobid"].astype(int)

applications_today  = anti_join(applications_today, applications_prev,['Jobid'])

# Cleaning the dataset 
applications_today =applications_today.loc[
    :, ~applications_today .columns.str.contains('^Unnamed')]
applications_today =applications_today .loc[
    :, ~applications_today.columns.str.contains('_y$')]
applications_today.columns = applications_today.columns.str.rstrip('_x') 
                            
##### Excluding job openings with a salary above a fixed quantity

applications_today['length'] = applications_today['Maxsalary'].apply(str)
applications_today = applications_today[
      (applications_today['Maxsalary'] <= 30000) 
    | (applications_today['length'] == 'nan')]

del applications_today['length']

#### Excluding more than two job openings from the same employer on the same day

# applications_today.to_csv("applications_today_pre_filter.csv")

applications_today=applications_today.drop_duplicates(
    subset=["employerName"], 
    keep='last', 
    inplace=False)

##############################################################################
# Randomly choosing job openings
##############################################################################

index = applications_today.index
number_of_rows = len(index)
div = int(number_of_rows/cruk_numberofferstoday)
n = random.randint(0,div)

if number_of_rows<cruk_numberofferstoday:
    a_list = list(range(1, div, 1))
else:
    a_list = list(range(int(n), int(div)*int(cruk_numberofferstoday), int(div)))

applications_today = applications_today.iloc[a_list]

##############################################################################
# Randomly assigning characteristics to job openings
##############################################################################

applications_today = applications_today.assign(race=1)
applications_today = applications_today.assign(gender=1)
applications_today = applications_today.assign(profile0=999)
applications_today = applications_today.assign(first='hello')

# race
race_series = applications_today.race.apply(
    lambda x: random.choice(['B', 'W']) ) 
applications_today.loc[:,['race']] = race_series

# gender 
gender_series = applications_today.gender.apply(
    lambda x: random.choice(['W', 'M']) ) 
applications_today.loc[:,['gender']] = gender_series

# Random number

profile_series=applications_today.profile0.apply(
    lambda x: random.randint(1, 100) ) 
applications_today.loc[:,['profile0']] = profile_series

# first candidate to apply.
first_series = applications_today.gender.apply(
    lambda x: random.choice(['Criminal records', 'Control']) ) 
applications_today.loc[:,['first']] = first_series

##############################################################################
# Creating the final dataset
##############################################################################

#### Inserting 'empty' or 'prefilled' columns that might be useful for the user.

applications_today['Password'] = 'xxxx'   
applications_today['Not_applied_reason'] = ''
applications_today['type_of_request'] = ''
applications_today['Antidiscrimination_policy'] = ''
applications_today['date_application']=datetoday
applications_today['Question_CR?']=''                                 
applications_today['Mention_CBC?']=''                                             


#### Deleting unnecesary columns

applications_today = applications_today.drop(columns=[
                                 'employerId',
                                 'Maxsalary',
                                 'Date',
                                 'Description',
                                 'Minsalary',
                                 'currency',
                                 'applications',
                                 'Location',
                                 'concept_original',
                                 'first_seen_date',
                                 'first_seen_time',
                                ])


#### Reordering columns

applications_today = applications_today[['Jobid',
                                         'employerName',
                                         'Job',
                                         'ExpirationDate',
                                         'url',
                                         'Password',
                                         'location_original',
                                         'race',
                                         'gender',
                                         'profile0',
                                         'first',
                                         'Description_full',
                                         'Not_applied_reason',
                                         'Reapply?',
                                         'Auditor',
                                         'date_application',
                                         'A1_Email',
                                         'A1_Date',
                                         'A1_Time',
                                         'A2_Email',
                                         'A2_Date',
                                         'A2_Time',
                                         'type_of_request',
                                         'Cover_letter?',
                                         'Question_CR?',
                                         'Mention_CBC?',
                                         'Financial_assets?',
                                         'Contact_clients?',
                                         'Children?',
                                         'Vulnerable?',
                                         'job_postcode',
                                         'Antidiscrimination_policy',
                                         'Observations',
                                         ]]


# Saving file
namefile = path0 + "/applications" + datetoday2 + '_' + time2 + ".csv" 
applications_today.to_csv(namefile, index=False, encoding='utf-8-sig', sep=';')

index3 = applications_today.index
number_of_rows3 = len(index3)

# Erase folder on which we saved the folders used during the research.

shutil.rmtree(path) 

print(datetoday + ": Selecting applications is finnished!")
