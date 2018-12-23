#import requests to deal with API responses
import requests
#import for json formated responses
import json
#import for XML formated responses
import xml.etree.ElementTree as ET
#import for datetime
import datetime
#import for geodecoding
from geopy.geocoders import Nominatim
import geocoder
#import for dataframe structures 
import pandas as pd
#import for missing value (np.nan) functionality
import numpy as np


'''this function 'getAllTransactions()' will return a dictionay of customer id as a key and customer name as value
in case the request to the API was a success, otherwise it will return None'''
def getAllTransactions():
    url = 'https://df-alpha.bk.rw/interview01/transactions'
    response = requests.get(url)
    if(response.status_code == 200): # 
        return json.loads(response.content.decode('utf-8'))
    else:
        return None

'''this function 'getAllCustomers()' will return a list of transactions, where each transaction is a dictionary 
with different value, in case the request to the API was successful, otherwise it will return None'''
def getAllCustomers():
    #initialize a dictionary to store customer's id & name for quick access
    customersInfo = {}
    url = 'https://df-alpha.bk.rw/interview01/customers'
    XMLresponse = requests.get(url)
    if(XMLresponse.status_code == 200):
        customersData = ET.fromstring(XMLresponse.content)
        for customer in customersData.findall('customer'):
            customerId = int(customer.find('id').text)
            customerName = customer.find('name').text
            #add only those who were not already in the dictionary
            if(not customerId in customersInfo):
                customersInfo[customerId] = customerName
            else:
                continue
        return customersInfo
    else:
        return None

'''this function 'getCityFromNominatim(address)' ectracts the city name from the 
geopy library's returned string address'''
def getCityFromNominatim(address):
    addrContent = address.split(',')
    addrSize = len(addrContent)
    cityName = addrContent[addrSize-3] #city is located at third place from the end
    return cityName


#getting and storing responses in variables - for analysis
transactionsList = getAllTransactions()
customers = getAllCustomers()

#initialize transactions and city_totals dataframe to store transactions.csv
transactionsData = pd.DataFrame(columns=('Transaction_Id', 'DateTime','Customer_Id',\
'Customer_Name','Amount','City_Name'))
cityData = pd.DataFrame(columns=('City_Name','Total_Amount','Unique_Customers',\
'Total_Transactions'))

#declare a dictionary for cities and their related data; city name as key and cityValues as value
cities = dict()

'''loop through all transactions to get the summaries only if 
the requests to the API were successful and both transactions and customers 
responses were not empty'''
if(isinstance(transactionsList,list) and len(transactionsList)>0\
 and isinstance(customers,dict) and len(customers)>0):
    id = 0 #transaction ids set to start from 0
    for transaction in transactionsList:
        #Part 1: PROCESS DATA FOR TRANSACTIONS SUMMARY
        transactionId = id
        timestamp = transaction.get('timestamp')
        datetime = str(pd.to_datetime(timestamp, unit='ms').round('S'))
        customerId = int(transaction.get('customerId'))
        customerName = customers.get(customerId)
        amount = float(transaction.get('amount'))
        lat = transaction.get('latitude')
        longit = transaction.get('longitude')
        #get location from googlr map
        locat = geocoder.google([lat, longit], method='reverse')
        #when google map api does not fail
        if(isinstance(locat,str)):
            cityName = locat.city 
        else: #when google map api fails, we use another library -geopy
            coordinate = str(lat)+","+str(longit)
            geolocator = Nominatim(user_agent="bankCoApp")
            location = geolocator.reverse(coordinate)
            address = location.address
            cityName = getCityFromNominatim(address)
        #insert transactions data in the created dataframe
        transactionsData.loc[id] = [transactionId,datetime,customerId,customerName,\
        round(amount,2),cityName] 
        #increment id as index for the next transaction id
        id+=1
        
        # Part 2: PROCESS DATA FOR CITY_VALUES SUMMARY
        # declare and initialize a dictionary to store all data values for a single city
        cityValues = {'amount': 0.0, 'uniqueCustIds':[], 'uniqueTransIds':[]}
        # add a new city in cities dictionary alongside its first values 
        if(not cityName in cities.keys()):
            cityValues['amount'] = amount
            cityValues['uniqueCustIds'] = [customerId]
            cityValues['uniqueTransIds'] = [transactionId]
            cities[cityName]= cityValues
        else: # update the already existing city data values 
            cityVal = cities[cityName]
            cityVal['amount'] += amount
            # only consider unique customer id
            if(not customerId in cityVal['uniqueCustIds']):
                cityVal['uniqueCustIds'].append(customerId) 
            # only consider unique transaction id 
            if(not transactionId in cityVal['uniqueTransIds']):
                cityVal['uniqueTransIds'].append(transactionId)
            # update the cities dictionary with new values
            cities[cityName]= cityVal

    #creating city integer, starting from 1, for city_totals summary
    city_id = 1
    cityIds = {} # dictionary to store cityId as key and cityName as value
    for city in cities.keys():
        cityIds[city_id] = city
        city_id += 1

    #Loop through the dictionary of cities and their ids to create a dataframe
    rowCount = 0 # used for dataframe index 
    for city_number, cityName in cityIds.items():
        cityData.loc[rowCount] = [str(city_number),round(cities.get(cityName).get('amount'),2),\
        str(len(cities.get(cityName).get('uniqueCustIds'))),str(len(cities.get(cityName).get('uniqueTransIds')))]
        rowCount +=1 # increment the index for the next data 
    #changing string values to int
    #pd.to_numeric(cityData)

    #producing summaries
    transactionsData.to_csv('TRANSACTIONS.csv', sep=',', encoding='utf-8',index=False)
    cityData.to_csv('CITY_TOTALS.csv', sep=',', encoding='utf-8',index=False)