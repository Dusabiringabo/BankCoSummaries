# BankCoSummaries
Description on the use of the ‘bankCoSummaries.py’ script

Introduction

The ‘bankCoSummaries.py’ is a python script that fetches data from A JSON list of transactions at https://df-alpha.bk.rw/interview01/transactions and An XML list of customers: https://df-alpha.bk.rw/interview01/customers. If the requests are successful; it produces two summaries files: TRANSACTIONS.CSV and CITY_TOTALS.CSV in the same folder as the script was run from, otherwise no file is produced.

Required libraries

For the script to run effectively, a user must install, through the command line, the following libraries by using ‘pip install’ followed by library name among pandas, numpy, geopy, and geocoder. Example: pip install pandas. In addition to that, python 3 must be installed.

Assumptions
•	All transactions from the API are unique; no duplicates.

Run the script
This script is run as other python scripts; the user needs to go in the folder where the file is stored and type the following in the terminal/command prompt: python bankCoSummaries.py. Once the file is successfully executed, the two files summary will be automatically created in the same folder.

Note
•	Opening the resulting csv files in Microsoft excel may change the date format. The actual content can be viewed by opening with other file openers such as Notepad, Libre Office, …
