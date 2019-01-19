# I use python3 with anaconda to simplify everything

import pandas as pd
import numpy as np
import os
import sys
import csv
import datetime 

script_dir = os.path.abspath(os.path.dirname(sys.argv[0]))

# I don't really understand why there are two databases that are slightly different. 
# Ham digital is missing columns, so not as good.

# encoding isn't UTF-8, I'm guessing 8859-1 (maybe CP 1252, but hopefully not as this is a web app)
radioid_contacts = pd.read_csv("https://www.radioid.net/static/users_quoted.csv", encoding="ISO-8859-1")

print("Radio ID raw length", len(radioid_contacts))
# header is repeated occasionally
radioid_contacts = radioid_contacts[radioid_contacts['Radio ID']!='Radio ID']
radioid_contacts['Radio ID'] = pd.to_numeric(radioid_contacts['Radio ID'])

print("Radio ID post header scrub", len(radioid_contacts))

ham_digital_contacts = pd.read_csv("https://ham-digital.org/status/users_quoted.csv", 
                                    encoding="ISO-8859-1",
                                    names=["Radio ID", "Callsign", "Name", "City", "State", "Country", "Remarks"])
print("Ham digital length:", len(ham_digital_contacts))

with open("DigitalContactList_UpdateTime.txt", mode="w") as updated_at:
    updated_at.write("%sZ" % datetime.datetime.utcnow())

print("Only using radioid")
all_contacts = radioid_contacts
#all_contacts = radioid_contacts.append(ham_digital_contacts)

#all_contacts = pd.read_csv("C:/Users/chris/Downloads/users_quoted.csv", encoding="ISO-8859-1")

# columns from RadioID:
# Radio ID	Callsign	Name	City	State	Country	Remarks

# Format expected by the CPS tool
# No.	Radio ID	Callsign	Name	City	State	Country	Remarks	Call Type	Call Alert

# We want "Private Call' in 'Call Type' for all these
# 'Call Alert' set to None
# No is just sequential starting with 1

all_contacts['No.'] = np.arange(1, len(all_contacts) + 1)
all_contacts['Call Type'] = "Private Call"
all_contacts['Call Alert'] = "None"

all_contacts['Name'] = all_contacts['Name'].str[:16].str.strip()
all_contacts['City'] = all_contacts['City'].str[:15].str.strip()
all_contacts['State'] = all_contacts['State'].str[:16].str.strip()
all_contacts['Country'] = all_contacts['Country'].str[:16].str.strip()
all_contacts['Remarks'] = all_contacts['Remarks'].str[:16].str.strip()

w = all_contacts[all_contacts['Callsign']=='VE3VGN']

# Name is max 16 chars
# Perry Marvin Rub
# Change the order to match export so diffs will work
correct_columns = ["No.","Radio ID","Callsign","Name","City","State","Country","Remarks","Call Type","Call Alert"]
all_contacts = all_contacts.sort_values(by="Radio ID") \
                            .reindex(columns=correct_columns)


csv_path = os.path.join(script_dir, "../csv_files/DigitalContactList.CSV")
csv_path_gen = os.path.join(script_dir, "../csv_files/DigitalContactListGenerated.CSV")

# CPS parser will split on the space between first and last name
# if strings aren't quoted 
# This encoding still doesn't round trip correctly. I'm thinking the phone
# might just do ascii.
# But that means doing a conversion like
#https://stackoverflow.com/questions/42302383/error-when-reading-utf-8-characters-with-python
import unicodedata
def filt(word):
    return unicodedata.normalize('NFKD', word).encode('ascii', errors='ignore').decode('ascii')

# switch back to UTF-8
# The CPS doens't deal with ISO-8859-1 any better and it simplifies my workflow
# because Meld defaults to UTF-8
all_contacts.to_csv(csv_path, index=False, quoting = csv.QUOTE_ALL, encoding="utf-8")
# save off the generated copy to make comparisons with CPS roundtrip easier
all_contacts.to_csv(csv_path_gen, index=False, quoting = csv.QUOTE_ALL, encoding="utf-8")