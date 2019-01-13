import pandas as pd
import numpy as np
import os
import sys
import re
import csv

script_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
talkgroups_path = os.path.join(script_dir, "data", "TG Decks.xlsx")
repeaters_path = os.path.join(script_dir, "data", "Repeaters-PNWDigital.xlsx")

talkgroups_all = pd.read_excel(talkgroups_path, sheet_name="Summary")

repeaters_path = os.path.join(script_dir, "data", "Repeaters-PNWDigital.xlsx")

repeaters = pd.read_excel(repeaters_path)

repeaters.columns = ['State', 'RepeaterDesc', 'LocationMap', 'Junk', 'FrequencyDesc']
repeaters.drop("Junk", inplace=True, axis=1)
# first row is from the weird formatting from the wiki
# mostly NAN
repeaters.drop(0, inplace=True)

# now parse repeater desc
# remove 'html'
# strip it
# split on the '-' character to have City, RepeaterName
# New Westminster doesn't have a name, go ahead and remove it
clean_repeaters = repeaters[repeaters['RepeaterDesc']!="New Westminster"].copy()
    
clean_repeaters['City'] = clean_repeaters['RepeaterDesc'].str.split("-").str[0].str.strip()
clean_repeaters['Name'] = clean_repeaters['RepeaterDesc'].str.split("-").str[1].str.strip()

# some of these are Nan because repeater offline
clean_repeaters['Transmit Frequency']=clean_repeaters['FrequencyDesc'].str.extract('(\d*\.\d+)', expand = True)

# offset
clean_repeaters['Offset']=clean_repeaters['FrequencyDesc'].str.extract('([\+\-]\.?\d)', expand = True)

clean_repeaters['Receive Frequency']=clean_repeaters['Transmit Frequency'].astype('float64') + clean_repeaters['Offset'].astype('float64')                
clean_repeaters['Transmit Frequency'].astype('float64')
#color code
clean_repeaters['Color Code']=clean_repeaters['FrequencyDesc'].str.extract('CC(\d)', expand = True)
clean_repeaters['Repeater Name'] = clean_repeaters['Name'].str.cat(clean_repeaters['City'], " ")
final_repeaters = clean_repeaters[['City', 'Repeater Name', 'Transmit Frequency', 'Receive Frequency', 'Color Code']].dropna()

# final formatting needed to join with matrix to make Channel.csv
# Columns:
# No.
# Channel Name
# Contact (Needs to match Talkgroups.csv)
# Receive Frequency
# Transmit Frequency
# Color Code
# Scan List (Generally Repeater Name + City)
# Channel Type (always D-Digital)
# Transmit Power [Low, Mid, High, Turbo]
# Bandwidth (always 12.5K)
# CTCSS/DCS Decode (Off)
# CTCSS/DCS Encode (Off)

remove_me = ["Data / Private Call", "MCT/HO Enabled"]

t=talkgroups_all[~talkgroups_all["Talkgroup"].isin(remove_me)] \
              .melt(['Talkgroup', 'TG ID', 'TS'], var_name="ProgrammingGroup", value_name="TG Status")
              
# stash Net 2 to the side. The matrix isn't being kept up to date based on individual
# repeater owners, so just add it to every single one
net_2 = t[t['Talkgroup'] == 'Net 2 (bm)'].copy()
net_2['TG Status'] = 'Some'

# drop na and add net2 back in
talkgroups_clean=pd.concat([t.dropna(), net_2]).sort_values(by="ProgrammingGroup")

# restict to a subset that I care about
only_repeater_groups = ["Seattle"]

talkgroups_filter=talkgroups_clean[talkgroups_clean["ProgrammingGroup"].isin(only_repeater_groups)]

# Talkgroups.csv maps the RadioID via Name field.
# That is the Contact field in talkgroups_filter
# Extract the talkgroups.csv info from the main talkgroups matrix
talkgroups_csv = talkgroups_filter[["Talkgroup", "TG ID"]] \
                            .rename(columns = {"Talkgroup":"Name", "TG ID":"Radio ID"}) \
                            .sort_values(by="Name") \
                            .assign(**{"Call Type":"Group Call", "Call Alert":"None"} ) \
                            
talkgroups_csv['No.'] = np.arange(1, len(talkgroups_csv) + 1)                            

talkgroups_csv_path = os.path.join(script_dir, "../csv_files/TalkgroupsPY.CSV")
talkgroups_csv.to_csv(talkgroups_csv_path, index=False, quoting = csv.QUOTE_ALL)

# Phew, now join talkgroups with repeaters to make the actual Channel.csv table
# on ProgrammingName == City (OK for Seattle, but not total)
channels = final_repeaters.rename(columns={"City" : "ProgrammingGroup"}) \
                .merge(talkgroups_filter, on="ProgrammingGroup", how='inner') \
                .rename(columns = {"Talkgroup":"Contact"}) 

channels["Channel Name"] = channels["Contact"]
                
channels_csv_path = os.path.join(script_dir, "../csv_files/ChannelsPY.CSV")
channels.to_csv(channels_csv_path, index=False, quoting = csv.QUOTE_ALL)

# Ugh, everything needs to be added to Zone.csv or the channel doesn't
# show up on the radio.



