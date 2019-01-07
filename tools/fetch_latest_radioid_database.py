# I use python3 with anaconda to simplify everything

import pandas as pd
import numpy as np
import os
import sys
import csv
import datetime 

script_dir = os.path.abspath(os.path.dirname(sys.argv[0]))

# encoding isn't UTF-8, I'm guessing 8859-1 (maybe CP 1252, but hopefully not as this is a web app)
all_contacts = pd.read_csv("https://www.radioid.net/static/users_quoted.csv", encoding="ISO-8859-1")
with open("DigitalContactList_UpdateTime.txt", mode="w") as updated_at:
    updated_at.write("%sZ" % datetime.datetime.utcnow())

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

csv_path = os.path.join(script_dir, "../csv_files/DigitalContactList.CSV")

# CPS parser will split on the space between first and last name
# if strings aren't quoted 
all_contacts.to_csv(csv_path, index=False, quoting = csv.QUOTE_ALL)