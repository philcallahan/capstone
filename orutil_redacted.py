##################################
####### imports ######
##################################

#library imports
import pandas as pd
pd.set_option('display.max_rows', 250, 'display.max_columns', None) #set pd display options
import statistics as stat

import datetime as dt
from datetime import datetime, timedelta, date
import calendar

import numpy as np
import matplotlib.pyplot as plt #visualizations
from collections import OrderedDict #ordered dict library

#suppress warnings for depreciated fxns
import warnings
warnings.filterwarnings('once')


##################################################################################
######## Filters dataframe down to only needed columns, with datetime objs #######
##################################################################################

def filterSurgnDF(surgn_csv):

    #read in data as csv (faster than xlsx!)
    dfQ2 = pd.read_csv(surgn_csv, 
                usecols=['redacted_surgn_col_1', 'redacted_surgn_col_2',
                        'redacted_surgn_col_3', 'redacted_surgn_col_4', 'redacted_surgn_col_5',
                        'redacted_surgn_col_6', 'redacted_surgn_col_7', 'redacted_surgn_col_8',
                        'redacted_surgn_col_9', 'redacted_surgn_col_10', 'redacted_surgn_col_11',
                        'redacted_surgn_col_12', 'redacted_surgn_col_13'])

    #convert all csv date strings to datetime obj
    dfQ2['redacted_surgn_col_2'] = pd.to_datetime(dfQ2['redacted_surgn_col_2']).dt.date #convert back to dt obj
    dfQ2['redacted_surgn_col_3'] = pd.to_datetime(dfQ2['redacted_surgn_col_3']).dt.date #convert back to dt obj
    dfQ2['redacted_surgn_col_5'] = pd.to_datetime(dfQ2['redacted_surgn_col_5']).dt.date #convert back to dt obj
    dfQ2['redacted_surgn_col_6'] = pd.to_datetime(dfQ2['redacted_surgn_col_6']).dt.date #convert back to dt obj
    
    #convert projected OR time to int and fill w zero if NA
    dfQ2['redacted_surgn_col_13'] = dfQ2['redacted_surgn_col_13'].fillna(0)
    dfQ2['redacted_surgn_col_13'] = dfQ2['redacted_surgn_col_13'].astype(int)
 
    #add col for dow str
    dfQ2['DOW'] = pd.to_datetime(dfQ2['redacted_surgn_col_2']).dt.day_name() 
    
    return dfQ2

#get all surgeons
def getAllSurgns(filtSurgnDF):
    surgnList = []
    
    #remove dups
    surgnList = list(dict.fromkeys(filtSurgnDF['redacted_surgn_col_10']))
    
    return surgnList


##################################################################################
############ This function grabs all days surgeon had procedures scheduled #######
##################################################################################

def getSurgnDates(filtSurgnDF, prim_surgn):
    
    #get all cases for a selected surgeon
    dfAllSurgnCases = filtSurgnDF.loc[(filtSurgnDF['redacted_surgn_col_10'] == prim_surgn)]

    #create a list of days the surgeon was in surgery
    surgnDaysList = []
    for index, row in dfAllSurgnCases.iterrows():
        if row['redacted_surgn_col_2'] not in surgnDaysList:
            surgnDaysList.append(row['redacted_surgn_col_2'])
            surgnDaysList = list(dict.fromkeys(surgnDaysList)) #remove dups
    
    #create a key/val pair for dict of tallied cases per surgeon
    surgnDict = {}

    surgnDict[dfAllSurgnCases.iloc[0]['redacted_surgn_col_10']] = surgnDaysList
    surgnDict
    
    return surgnDict

##################################################################################
############ makes overall surgeon dict from the filtered dataset #######
##################################################################################

def makeSurgnDict(filtSurgnDF):
    surgnList = getAllSurgns(filtSurgnDF)
    
    surgnDict = {}
    for prim_surgn in surgnList:
        currSurgnDict = getSurgnDates(filtSurgnDF, prim_surgn)       
        surgnDict[prim_surgn] = currSurgnDict.values()
        
    return surgnDict

##################################################################################
######### tallies all dates of a specified DOW given the dict, surgn, dow ########
##################################################################################

def tallyDOW(surgnDict, owner, dow):
#     for owner in surgnDict:
    import calendar
    MTWTFlist = []
    for surgn in surgnDict[owner]:
        for d in surgn: 
            dayOfweek_num = d.weekday()
            dayOfweek = calendar.day_name[dayOfweek_num]

            if dayOfweek == dow:
                MTWTFlist.append(d)
    return MTWTFlist

##################################################################################
########## convert datetime obj to list of strings to input to other fxns #######
##################################################################################

def DOWtally2str(list_of_dates):
    list_of_date_strs = []
    for d in list_of_dates:
        dateStr = d.strftime("%Y-%m-%d")
        list_of_date_strs.append(dateStr)
        
    return list_of_date_strs


##################################################################################
########## get dict of all ORs and case nums - given surgeon and date ############
##################################################################################

def getSurgnORs(filtSurgnDF, prim_surgn, sched_date, verbose=False):
    
    #convert procedure date to datetime obj if it isn't
    if type(sched_date) is str:
        sched_date = pd.to_datetime(sched_date).date()
    
    #filter out df to surgeon and sched_date
    surgnDF = filtSurgnDF.loc[(filtSurgnDF['redacted_surgn_col_10'] == prim_surgn)]
    surgnDF = surgnDF.loc[(filtSurgnDF['redacted_surgn_col_2'] == sched_date)]
    
    #get the OR num and add to dict
    ORdict = {}
    ORlist = []
    for i, s in surgnDF.iterrows(): #iterate over df rows

        if verbose:
            pass
        if ~np.isnan(s[7]): #if redacted_surgn_col_8 has a val...

            if s[3] == 'Scheduled':
                if verbose:
#                     print('ENTERED Scheduled loop!!!!!!!!!!!!!')
                    pass
                ORdict[s[0]] = int(s[7])
            elif s[3] == 'Moved':
                if verbose:
#                     print('ENTERED MOVED loop!!!!!!!!!!!!!')
                    pass
                if s[6] != s[7]:
                    if verbose:
#                         print('MOVED TO DIFF OR!!!!!!!!!!!!!!!!!!')
                        pass
                    ORdict[s[0]] = 'Moved_OR'

        elif np.isnan(s[7]): #if redacted_surgn_col_8 has NO val
            if s[3] == 'Removed':
                ORdict[s[0]] = 'Removed'
            elif s[3] == 'Canceled':
                ORdict[s[0]] = 'Canceled'
            elif s[3] == 'Moved':
                ORdict[s[0]] = 'Moved_OR'
    
    if verbose:
        # make list with no dups
        ORlist_with_actions = list(set(ORdict.values()))
        print(f'ORlist_with_actions:', ORlist_with_actions)
    
    ##remove all 'Removed', 'Moved_OR', and 'Canceled' from list
    for k, v in list(ORdict.items()):
        if type(v) ==  str:
            del ORdict[k]
    
    # make list with no dups
    ORlist = list(set(ORdict.values()))
    
    return ORlist, ORdict

####################################################################
####### make dict of all rooms surgeon worked in on sched_date #####
####################################################################


def makeSurgnDOWORdict(filtSurgnDF, prim_surgn, dow, list_of_date_strs, verbose=False):
    ORdict2 = {}

    for d in list_of_date_strs:
        if verbose:
#             print('d:', d)
            pass
        ORsUsed = getSurgnORs(filtSurgnDF, prim_surgn, d)[0]
        if verbose:
#             print(f'ORsUsed:', ORsUsed)
            pass
        ORdict2[(prim_surgn, dow, d)] = ORsUsed
        
    #clean up the k,v pairs with no vals
    for k in ORdict2.copy():
        if not ORdict2[k]:
            ORdict2.pop(k)

    return ORdict2

######################################################################
####### create list of only unique ORs used given surgnDOWORdict #####
######################################################################
#NOTE: uses makeSurgnDOWORdict fxn !!!!!!!!!!!!!!!!!!

def getUniqueORs(surgnDOWORdict):
    ORsUsed = []
    for ORs in surgnDOWORdict.values():

        if ORs != []:
            if len(ORs) == 1:
                ORsUsed.append(ORs[0])
            else:
                for OR in ORs:
                    ORsUsed.append(OR)

    uniqueORs = list(set(ORsUsed)) #remove dups
    return uniqueORs

#############################################################################################
####### makes dict of dates worked for all surgeon, dow (values not specific to OR yet) #####
#############################################################################################
#uses tallyDOW
#uses DOWtally2str
#uses makeSurgnDOWORdict
#uses getUniqueORs

def make_unspec_pop_dict(filtSurgnDF, surgnDict, dowList):
    surgn_dow_dict = {}
    for prim_surgn in surgnDict:
        for dow in dowList:
            sched_dates_on_dow = tallyDOW(surgnDict, prim_surgn, dow)
            list_of_date_strs = DOWtally2str(sched_dates_on_dow)
            surgnDOWORdict = makeSurgnDOWORdict(filtSurgnDF, prim_surgn, dow, list_of_date_strs)
            uniqueORs = getUniqueORs(surgnDOWORdict)
            for uORs in uniqueORs:
                surgn_dow_dict[(prim_surgn, dow, uORs)] = [list_of_date_strs]
    return surgn_dow_dict

######################################################################
####### corrects values in unspec pop dict to reflect OR #########
######################################################################
#uses getSurgnORs

def spec_pop_dict(filtSurgnDF, unspecPopDict):
    updatedDict = {}
    for key in unspecPopDict:
        keydf = filtSurgnDF.loc[filtSurgnDF['redacted_surgn_col_10'] == key[0]]
        keydf = filtSurgnDF.loc[filtSurgnDF['DOW'] == key[1]]
        for val in unspecPopDict[key]:
            updated_val_list = []
            for sched_date in val:
                ORsUsed, casesDict = getSurgnORs(keydf, key[0], sched_date)

                if key[2] in ORsUsed:
                    updated_val_list.append(sched_date)

            updatedDict[key] = updated_val_list
        
    return updatedDict


######################################################################
####### filters snapshot csv to useable dataframe #########
######################################################################

def filterSnapDF(snapshot_csv_path):
    #read in data as csv (faster than xlsx!)
    df_snap = pd.read_csv(snapshot_csv_path, 
                    usecols=['redacted_snap_col_1', 'redacted_snap_col_2',
                            'redacted_snap_col_3', 'redacted_snap_col_4', 'redacted_snap_col_5',
                            'redacted_snap_col_6', 'redacted_snap_col_8', 'redacted_snap_col_7'])

    #convert all csv date strings to datetime obj
    df_snap['redacted_snap_col_2'] = pd.to_datetime(df_snap['redacted_snap_col_2']).dt.date #convert back to dt obj
    df_snap['redacted_snap_col_3'] = df_snap['redacted_snap_col_3'].astype(str)
        
    #add col for dow str
    df_snap['DOW'] = pd.to_datetime(df_snap['redacted_snap_col_2']).dt.day_name() 
    
    return df_snap

######################################################################
#### remove dates that exist in surgn data but not in snapshot data
#### this means procedure was ultimately canceled, or removed on that day
#### it was in there because at one point it WAS scheduled on that day
######################################################################


def removeEmptyDFs(popDict, filtSnapDF, verbose=False):

    #pull cols out as lists to check if date/roomID combos exist
    snap_dates_list = list(filtSnapDF['redacted_snap_col_2'])
    if verbose:
#         print(snap_dates_list[0:50])
        pass

    roomID_list = list(filtSnapDF['redacted_snap_col_3'])
    if verbose:
#         print(roomID_list[0:50])
        pass
    
    popDict_no_empties = {}
    #iterate through popDict keys
    for key in popDict:
        if verbose:
            print(f'key:', key)
            pass
        
        updatedList = []
        #iterate through each val date
        for val in popDict[key]:
            filterByDate = datetime.strptime(val, '%Y-%m-%d').date() #convert filterByDate to dt obj
            roomID = key[2]
            
            df_filtered_by_date = filtSnapDF.loc[(filtSnapDF['redacted_snap_col_2'] == filterByDate)]
            df_filtered_by_date_roomID = df_filtered_by_date.loc[(df_filtered_by_date['redacted_snap_col_3'] == str(key[2]))]

            if not df_filtered_by_date_roomID.empty:
                updatedList.append(val)
                if verbose:
                    print(filterByDate, 'produces an empty dataframe?:', df_filtered_by_date_roomID.empty)
                    pass
        popDict_no_empties[key] = updatedList
        
    return popDict_no_empties


######################################################################
####### tallies values (aka blocks or dates) in popDict #########
######################################################################

def tally_popDict_dates(popDict_no_empties, verbose=False):
    talliedDict = {}
    for key in popDict_no_empties:
        if verbose:
            print(key, ':', popDict_no_empties[key])
            pass
        if popDict_no_empties[key] != []:
            if verbose:
                print(f'This key is NOT empty:', key)
                print('---------------------')
                pass
            val = popDict_no_empties[key]
            talliedDict[key] = len(val)
    return talliedDict


######################################################################
####### makes the talliedDict a dataframe #########
######################################################################

def makeTalliedDictDF(talliedDict):
    pop_key_list = list(zip(*talliedDict.keys())) #unzips the keys
    pop_tally_list = list(talliedDict.values())

    popdf = pd.DataFrame({'surgeon':pop_key_list[0],
                         'dow':pop_key_list[1],
                         'op_room':pop_key_list[2],
                         'blocks':pop_tally_list})
    return popdf

##################################################################################################################
###################### CREATES TRENDLINES FROM CASES and MINUTES ##################################################
##################################################################################################################

######################################################################
####### create the find blocks fxn - given owner, roomID, dow ########
######################################################################

def find_blocks(popDict_no_empties, owner, dow=None, ORnum=None):
    blocks_dict = {}
    for key in popDict_no_empties:
        # in no dow/roomID provided ---------------------- 1
        # add all owners to blocks_dict
        if (dow == None and ORnum == None) :
            if (owner == key[0]): 
                blocks_dict[key] = popDict_no_empties[key]
                
        # if no OR provided ------------------------------- 2
        #add all owner/dow combos to blocks_dict
        elif ORnum == None:
            if (owner == key[0] and dow == key[1]): 
                blocks_dict[key] = popDict_no_empties[key]
            
        # if key matches all three criteria ---------------- 3
        # add all owner/dow/OR combos to blocks_dict (should be only 1)
        elif (owner == key[0] and dow == key[1] and ORnum == key[2]): 
            blocks_dict[key] = popDict_no_empties[key]
            
    return blocks_dict 


######################################################################
####### get case info - given date, OR ############################
######################################################################

def blockDict_per_OR_and_date(filtSurgnDF, filtSnapDF, ORnum, filterByDate, verbose=False):
    
    #date to filter by ------------------------
    dateObj = datetime.strptime(filterByDate, '%Y-%m-%d').date() #convert filterByDate to dt obj
    dfSDate1 = filtSnapDF.loc[(filtSnapDF['redacted_snap_col_2'] == dateObj)]
    
    #ORnum to filter by
    dfSDate1 = dfSDate1.loc[(dfSDate1['redacted_snap_col_3'] == str(ORnum))] #--------------------------------------------------

    if dfSDate1.empty:
        if verbose:
            print(filterByDate+':', 'Dataframe contents are empty!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        pass
    
    dfSDate1_recover = dfSDate1.copy()
    
    dfSDate1 = dfSDate1.loc[(dfSDate1['redacted_snap_col_1'] == 'redacted_snap_val_1') |
                       (dfSDate1['redacted_snap_col_1'] == 'redacted_snap_val_2')]
    
    if dfSDate1.empty:###########################################################
        ###############################
        ### get denom ---------------
        ###############################
        if verbose:
            print(filterByDate+':', 'NO procedure ID mins, using log ID!!!!!!!!!!!!!!')
            print(f'dfSDate1_recover:', dfSDate1_recover)
        pass
        denom_alt_df = filtSurgnDF.loc[(filtSurgnDF['redacted_surgn_col_1'] == int(dfSDate1_recover['redacted_snap_col_8'].iloc[0]))]
        denom_alt = denom_alt_df['redacted_surgn_col_13'].iloc[0]
        denom = int(denom_alt)
        if verbose:
            print('denom_alt_df:', denom_alt_df)
        
        ##################################
        ### get numer -------------------
        ##################################


        # Use GroupBy() to compute the sum
        dfSummedMins = dfSDate1_recover.groupby('redacted_snap_col_8', as_index=False).sum()
        if verbose:
            print(f'dfSummedMins:', dfSummedMins)
        #convert caseID to int
        dfSummedMins['redacted_snap_col_8'] = dfSummedMins['redacted_snap_col_8'].astype(int)

        #new df with only data needed
        dfCaseMins = dfSummedMins[['redacted_snap_col_8', 'redacted_snap_col_7']].copy()
        numer = dfCaseMins['redacted_snap_col_7'].sum()

        #create dict of case and time
        df4Dict = pd.DataFrame({'mins':list(dfCaseMins['redacted_snap_col_7'])}, index=dfCaseMins['redacted_snap_col_8'])
        df4Dict['mins']
        ORdateBlockDict = df4Dict['mins'].to_dict()
        ORdateBlockDict
        
    else: ####################################################################
        #########################################
        ### get denominator ---------------------
        #########################################
        exist_block = list(dfSDate1['redacted_snap_col_4']).count('redacted_snap_val_3') #check if BLOCK type exists
        exist_man = list(dfSDate1['redacted_snap_col_4']).count('redacted_snap_val_4') #check if MANREL type exists
        exist_out = list(dfSDate1['redacted_snap_col_4']).count('redacted_snap_val_5') #check if OUTSIDE type exists
        exist_over = list(dfSDate1['redacted_snap_col_4']).count('redacted_snap_val_6') #check if OVERBOOK type exists
        exist_cor = list(dfSDate1['redacted_snap_col_4']).count('redacted_snap_val_7') #check if CORRECT type exists

        if exist_block >= 1:
            if verbose:
                print(filterByDate+':', 'block here ♥')
                pass #keep here to comment out prints without getting stuck
            totBlockMins = dfSDate1.loc[dfSDate1['redacted_snap_col_4'] == 'redacted_snap_val_3', 'redacted_snap_col_7']
            denom = totBlockMins.iloc[0]
        #     print(f'denom:', denom) #tp

        elif exist_man >= 1:
            if verbose:
                print(filterByDate+':', 'man here ♠')
                pass #keep here to comment out prints without getting stuck
            totBlockMins = dfSDate1.loc[dfSDate1['redacted_snap_col_4'] == 'redacted_snap_val_4', 'redacted_snap_col_7']
            denom = totBlockMins.iloc[0]
        #     print(f'denom:', denom) #tp

        elif exist_out >= 1:
            if verbose:
                print(filterByDate+':', 'out here ♣ - mins not in surgn_csv')
                pass #keep here to comment out prints without getting stuck
            totBlockMins = dfSDate1.loc[dfSDate1['redacted_snap_col_4'] == 'redacted_snap_val_5', 'redacted_snap_col_7']
            talliedBlockMins = sum(list(totBlockMins))
            denom = talliedBlockMins

        elif exist_cor >= 1 & exist_over >=1:
            if verbose:
                print(filterByDate+':', 'cor and over redacted_snap_col_4 here ♦ ')
                pass #keep here to comment out prints without getting stuck
            totBlockMins = dfSDate1.loc[(dfSDate1['redacted_snap_col_4'] == 'redacted_snap_val_7')|
                                        (dfSDate1['redacted_snap_col_4'] == 'redacted_snap_val_6'), 'redacted_snap_col_7']
            if verbose:
                print(f'totBlockMins:', totBlockMins)
                pass
            talliedBlockMins = sum(list(totBlockMins))
            denom = talliedBlockMins

        elif exist_cor >= 1:
            if verbose:
                print(filterByDate+':', 'cor redacted_snap_col_4 here ♦ ')
                pass #keep here to comment out prints without getting stuck
            totBlockMins = dfSDate1.loc[(dfSDate1['redacted_snap_col_4'] == 'redacted_snap_val_7'), 'redacted_snap_col_7']
            if verbose:
                print(f'totBlockMins:', totBlockMins)
                pass
            talliedBlockMins = sum(list(totBlockMins))
            denom = talliedBlockMins

        else: #sometimes BLOCK template doesnt exist?
            if verbose:
                print(filterByDate+':', 'no block redacted_snap_col_4!!!!!!!!!!!!')
                print('dfSDate1[redacted_snap_col_6]:', dfSDate1)
                pass #keep here to comment out prints without getting stuck
            denom_alt_df = filtSurgnDF.loc[(filtSurgnDF['redacted_surgn_col_1'] == int(dfSDate1['redacted_snap_col_6'].iloc[0]))]
            denom_alt = denom_alt_df['redacted_surgn_col_13'].iloc[0]
            denom = int(denom_alt)
            if verbose:
                print('denom_alt_df:', denom_alt_df)

        ##########################
        ### get numer ##################
        ##########################

        # Use GroupBy() to compute the sum
        dfSummedMins = dfSDate1.groupby('redacted_snap_col_6', as_index=False).sum()
    #     print(f'dfSummedMins:', dfSummedMins)

        #convert caseID to int
        dfSummedMins['redacted_snap_col_6'] = dfSummedMins['redacted_snap_col_6'].astype(int)
    #     print(f'dfSummedMins:', dfSummedMins) #tp

        #new df with only data needed
        dfCaseMins = dfSummedMins[['redacted_snap_col_6', 'redacted_snap_col_7']].copy()
        numer = dfCaseMins['redacted_snap_col_7'].sum()
    #     print(f'numer:', numer) #tp

        #create dict of case and time
        df4Dict = pd.DataFrame({'mins':list(dfCaseMins['redacted_snap_col_7'])}, index=dfCaseMins['redacted_snap_col_6'])
        df4Dict['mins']
        ORdateBlockDict = df4Dict['mins'].to_dict()
        ORdateBlockDict

    return numer, denom, ORdateBlockDict
    


######################################################################
####### filter fxn to filter surgeon_csv - given date, owner ########
######################################################################

def filterCases(filtered_surgn_df, filterByDate, prim_surg):
    dfQ2 = filtered_surgn_df
     
    #############################################
    # convert input to datetime obj -------------
    #############################################
    import datetime as dt
    from datetime import datetime, timedelta, date
    dateObj = datetime.strptime(filterByDate, '%Y-%m-%d').date()
#     print(f'dateObj:', dateObj) #tp
    
    ###############################################
    # filter df by certain columns ################
    ###############################################
    dfSDate2 = dfQ2.loc[dfQ2['redacted_surgn_col_2'] == dateObj]
    dfSDate2 = dfSDate2.loc[(dfSDate2['redacted_surgn_col_2'] == dfSDate2['redacted_surgn_col_6']) |
                            pd.isnull(dfSDate2['redacted_surgn_col_6'])]
    
    #filter procedure actions ---------------
    dfSDate2 = dfSDate2.loc[(dfSDate2['redacted_surgn_col_10'] == prim_surg)]
    dfSDate2 = dfSDate2.loc[(dfSDate2['redacted_surgn_col_4'] == 'Scheduled') | 
                      (dfSDate2['redacted_surgn_col_4'] == 'Removed')|
                      (dfSDate2['redacted_surgn_col_4'] == 'Canceled')]
    
    dfSDate2 = dfSDate2.loc[(dfSDate2['redacted_surgn_col_3']< dateObj)]
    dfSDate2 = dfSDate2.sort_values('redacted_surgn_col_3')


    # create key col for dict based off date --------------------
    dfSDate2['SCHED_DATE_KEY'] = (pd.to_datetime(dfSDate2['redacted_surgn_col_2'])).astype(str)
    dfSDate2['AUD_DATE_KEY'] = (pd.to_datetime(dfSDate2['redacted_surgn_col_3'])).astype(str)
    dfSDate2
    
    #now we can strip out anything that doesn't match procedure date
    dfSDate2 = dfSDate2.loc[(dfSDate2['redacted_surgn_col_2'] == dfSDate2['redacted_surgn_col_5']) |
                            pd.isnull(dfSDate2['redacted_surgn_col_5'])]

    
    return dateObj, dfSDate2

######################################################################
#######  CREATE TIMESERIES DICTIONARY - given sched_date ########
######################################################################

#creates ordered dictionary of action dates for specified room, sched date, and surgeon
# refactor if time - this was first dict fxn made so it's messy

def makeCaseDict(df, verbose=False):
    schDict = OrderedDict()
    audDict = OrderedDict()
    blockDict = OrderedDict()
    caseList = []
    removalList = []

    for i, j in df.iterrows(): #iterates over df
        currCase = j[0] #current procedure number
        currAD = j[-1] #current action date
        currSD = j[-2] #current SCHED_DATE_KEY
        currKey = str(j[10]+'-'+j[11]) #current caseList key

        #conditional to check if SCHEDULE_DATE exists in outer dict
        if currSD in schDict: #if it does, go to action date inner dict
            audDict = schDict.get(currSD) #update audDict to inner dict
            
            #conditional to see if action date is a key in inner dict
            if currAD in audDict: #if it is, check if caseList has procedure date
                blockDict = audDict.get(currAD)
                
                if currKey not in blockDict:
                    caseList = [currCase]
                    blockDict[currKey] = caseList
                    if verbose:
                        print('WARNING: DIFF SERVICE or op_room!!!!!!!!')
                    
                else:
                    if j.iloc[3] == 'Canceled':
                        if verbose: #troubleshooting print
                            print('Canceled')
                        caseList = list(set(caseList)) #remove dups
                        schDict[currSD][currAD][currKey] = caseList
                        if currCase in caseList:
                            caseList.remove(currCase) #remove currCase from caseList
                        removalList.append(currCase)
                        
                    elif j.iloc[3] == 'Removed':
                        if verbose: #troubleshooting print
                            print(f'Removed:', currCase)
                        caseList = list(set(caseList)) #remove dups
                        schDict[currSD][currAD][currKey] = caseList
                        if currCase in caseList:
                            caseList.remove(currCase) #remove currCase from caseList
                        removalList.append(currCase) 
                        
                    elif j.iloc[3] == 'Scheduled':
                        if verbose: #troubleshooting print
                            print(f'Scheduled:', currCase, 'but no currAD in list yet') #tp
                        caseList.append(currCase) #append to curr caseList
                        caseList = list(set(caseList)) #remove dups
                        schDict[currSD][currAD][currKey] = caseList
                        if currCase in removalList:
                            removalList.remove(currCase)

                    
            else: #if currAD NOT in audDict, create key/val pair in audDict
                if j.iloc[3] == 'Canceled':
                    if verbose: #troubleshooting print
                        print(f'Canceled:', currCase, 'but no currAD in list yet') #tp
                    caseList = list(set(caseList)) #remove dups
                    schDict[currSD][currAD] = {currKey:caseList}
                    if currCase in caseList:
                        caseList.remove(currCase) #remove currCase from caseList
                    removalList.append(currCase)
                    
                elif j.iloc[3] == 'Removed':
                    if verbose: #troubleshooting print
                        print(f'Removed:', currCase, 'but no currAD in list yet') #tp
                    if currCase in caseList:
                        caseList.remove(currCase) #remove currCase from caseList
                    removalList.append(currCase)
                    if verbose: #troubleshooting print
                        print(f'just added:', removalList, 'to removalList') #tp

                elif j.iloc[3] == 'Scheduled':
                    if verbose: #troubleshooting print
                        print(f'Scheduled:', currCase, 'but no currAD in list yet') #tp
                    caseList = list(set(caseList)) #remove dups
                    caseList.append(currCase)
                    caseList = list(set(caseList)) #remove dups
                    schDict[currSD][currAD] = {currKey:caseList}
                    if currCase in removalList:
                        removalList.remove(currCase)
                        if verbose:
                            print(f'just removed', currCase, 'from removalList')

                
        else: #if NOT, create key/val pair in schDict
            if verbose: #troubleshooting print
                print(f'Added currSD:', currSD, 'to schDict') #tp
            caseList = [currCase]
            blockDict[currKey] = caseList
            audDict[currAD] = blockDict
            schDict[currSD] = audDict
    if verbose:
        print(f'removalList:', removalList) #troubleshooting print
    return schDict #return entire outer dictionary

######################################################################
#######  aggregates multiple dates from key to plot in timeseries ####
######################################################################
#uses blockDict_per_OR_and_date

def agg_dates_to_plot(filtSurgnDF, filtSnapDF, owner_dow_OR_dict):
    agg_own_dow_OR_date_dict = {}
    
    for key in owner_dow_OR_dict:
        owner = key[0]
        dow = key[1]
        roomID = key[2]
        currDateList = owner_dow_OR_dict[key]

        #iterate through date list
        for date in currDateList:
            sched_date = date
            numer, denom, ORdateBlockDict = blockDict_per_OR_and_date(filtSurgnDF, filtSnapDF, roomID, sched_date, 
                                                                      verbose=False)
            agg_own_dow_OR_date_dict[(owner,dow,roomID,sched_date)] = {denom:ORdateBlockDict}
            
    return agg_own_dow_OR_date_dict


######################################################################
#######  AGGREGATE DICTS to PLOT per DATE ########
######################################################################
#uses filterCases
#uses makeCaseDict

def agg_plot_dicts_per_date(filtSurgnDF, agg_dates_to_plot, verbose=False):
    agg_plots_per_date = {}
    for i in agg_dates_to_plot:
        if verbose:
            print(i) #tp
        dummy_var, filtered_df = filterCases(filtSurgnDF, i[3], i[0])
        plotDict = makeCaseDict(filtered_df)
        agg_plots_per_date[i] = plotDict
    return agg_plots_per_date

######################################################################
####### take vals out of dict for plot  ########
######################################################################

#with conditional to accept empty dicts
def makeDictPlottable(dict_to_plot, verbose=False):
    date_key = []
    dateList = []
    numCases = []
    caseNums = []
    
    if dict_to_plot != OrderedDict():
        if verbose:
            print("not empty dict")
        date_key = list(dict_to_plot.keys())[0] #get scheduled date

        #tally everything into lists

        for i in dict_to_plot.keys():
            for j in dict_to_plot[i].keys():
                dateList.append(j) #create list of action dates where something happened
                for k in dict_to_plot[i][j]:
                    numCases.append(len(dict_to_plot[i][j][k])) #list of lists of cases to plot
                    caseNums.append(dict_to_plot[i][j][k]) #number of cases (if wanting to plot cases rather than mins)

    #if troubleshooting
    if verbose:
        print(f'dateList1:', dateList)
        print(f'numCases1:', numCases)
        print(f'caseNums1:', caseNums)
    
    return date_key, dateList, caseNums



#####################################################################################
####### accounts for canceled procedures which don't show up on snapshot_csv  ########
#######################################################################################

#this is a canceled case that doesn't appear in the first query.
def includeCancellations(filtered_df, list_of_lists_of_cases, dict_of_case_mins, verbose=False):
    for l in list_of_lists_of_cases:
        if verbose:
            print(f'l:', l)
            print(f'dict_of_case_mins:', dict_of_case_mins)
        for c in l:
            if verbose:
                print(f'c:', c)
            elif c not in dict_of_case_mins:
                expTimes = filtered_df.loc[filtered_df['redacted_surgn_col_1'] == c, 'redacted_surgn_col_13' ]
                if verbose:
                    print(f'expTimes:', expTimes)
                dict_of_case_mins[c] = expTimes.iloc[0]
    return dict_of_case_mins


######################################################################
######## convert caseNums to case minutes  ########
######################################################################

# convert caseNums to case minutes
def tallyCaseMins(list_of_lists_of_cases, dict_of_case_mins, verbose=False):
    accum_mins_list = []
    for l in list_of_lists_of_cases:
        if verbose:
            print(f'accumulated list:', l)
        if l !=[]:
            totMins = 0
            for case in l:
                totMins = totMins + dict_of_case_mins.get(case)
            accum_mins_list.append(totMins)

    return accum_mins_list

#NOTE: create numerator used for model (may be different than previously defined)
#because this numerator will be stored @11:59 night before schedule date
#if there is a cancellation ON schedule date numer1159 won't pick it up
#but that's okay because it's not part of project scope

######################################################################
####### convert minutes to percent of total  ########
######################################################################

#gets new numerator on night before surgery
def get_numer1159(accum_mins_list, verbose=False):
    numer1159 = 0
    
    if accum_mins_list != []:
        numer1159 = accum_mins_list[-1]
        
    return numer1159

######################################################################
####### convert minutes to percent of total  ########
######################################################################

def percentUtil(accum_mins_list, total_block_time):
    accum_percent_list = []
    for mins in accum_mins_list:
        percentUtil = mins/total_block_time
        accum_percent_list.append(percentUtil)
    return accum_percent_list

######################################################################
#### converts list of date strs (ie. action dates) to datetime objs ###
######################################################################

def makeDateObj(list_of_date_strings):
    dateOList =[]
    for d in list_of_date_strings:
        dateObj = datetime.strptime(d, '%Y-%m-%d').date()
        dateOList.append(dateObj)
    return dateOList

##################################################################
#### convert dates to days_back and store as dict of case nums ###
##################################################################

def makeDaysbackDict(schedule_date, list_of_date_objs, list_of_accum_percent_util, verbose=False):
    daysBackList = []
    for d in list_of_date_objs:
        if verbose:
            print(f'day in list_of_date_objs:', d) 
        schedDate = schedule_date
        daysBack = ((schedDate - d).days)+1
        daysBackList.append(-1*daysBack)

    #convert to dict
    dateDict = dict(zip(daysBackList, list_of_accum_percent_util)) #use minsList from above instead of cases!!!!!!!!!!!!!
    return dateDict

##################################################################
#### make empty n-day dict ####
##################################################################

def makeEmptyDict(num_lookback_days, verbose=False):
    
    revIdx = list(range(-(num_lookback_days),-0)) #number days back, keys
    revVals = [0 for i in range(num_lookback_days)] #fill vals with zeroes
    emptyDict = OrderedDict(zip(revIdx, revVals)) #make dict
    
    #troubleshooting
    if verbose:
        print(f'emptyDict:', emptyDict)  

    return emptyDict

####################################################################################
#### refine dict to have no dates older than n days back and tally any previous ####
####################################################################################

def limitDaysback(dict_to_limit, max_days_back, verbose=False):
    currHighval = 0
    for d in dict_to_limit:
        if verbose:
            print(f'd:', d) #test print
        if d < (max_days_back*(-1)):
            currval = dict_to_limit.get(d)
            if currval > currHighval:
                currHighval = currval
    return currHighval

##################################################################
#### put plot dict together ####
##################################################################

def assemblePlotDict(empty_dict, dict_of_proc_date_actions, tally_before_window):
    plotDict = OrderedDict()
    
    #iterate through empty_dict and fill when procedure action occurs
    for r in empty_dict:
        if r in dict_of_proc_date_actions:
            plotDict[r] = dict_of_proc_date_actions.get(r)
            tally_before_window = dict_of_proc_date_actions.get(r)
        else:
            plotDict[r] = tally_before_window 

    return plotDict


##############################################################################
#### takes agg_dates_to_plot AND plotDicts and combines to plottable dict ####
##############################################################################
#uses makeEmptyDict
#uses makeDictPlottable
#uses includeCancellations
#uses tallyCaseMins
#uses makeDateObj
#uses makeDaysbackDict


def ts_plots(filtered_df, agg_dates_to_plot, plotDicts, num_lookback_days, verbose=False):
    #make empty dicts to put x,y into
    emptyDict = makeEmptyDict(num_lookback_days)
    plotDays = list(emptyDict.keys())
    if verbose:
        print(f'Use days back as x:', plotDays)
    ts_dict = {}
    
    #iterate through each schedule date and prep to plot
    for key in plotDicts:
        if plotDicts[key].values() != []:
            denom = list(agg_dates_to_plot[key].keys())[0]
            if verbose:
                print(f'key:', key)
                print(f'denom:', denom)

            #prep the dict to plot
            date_key, dateList, caseNums = makeDictPlottable(plotDicts[key], verbose=False)
            if verbose:
                print(f'ORdateBlockDict(before):', caseNums)    
            ORdateBlockDict = list(agg_dates_to_plot[key].values())[0]
            if verbose:
                print(f'ORdateBlockDict (after):', ORdateBlockDict)
    #             print(f'filtered_df:', filtered_df) #test print

            #find projected time from surgn df and add to dict if there was a cancelation
            ORdateBlockDict = includeCancellations(filtered_df, caseNums, ORdateBlockDict)
    #         ts_dict[key] = ORdateBlockDict

            #tally the case minutes in order
            accum_mins_list = tallyCaseMins(caseNums, ORdateBlockDict, verbose=False)
            if verbose:
                print(f'accum_mins_list:', accum_mins_list)

            #some cases are canceled/resched day of so they appear in numer
            #project decided to omit those, hence create new numer1159 var
            numer1159 = get_numer1159(accum_mins_list)
            if verbose:
                print(f'numer1159:', numer1159)

            #use above helper fxn to convert mins list to percent util
            accum_percent_util = percentUtil(accum_mins_list, denom)
            if verbose:
                print(f'accum_percent_util:', accum_percent_util)

            #convert action dates list from strs back to datetime objs
            dateSubList = list(plotDicts[key].values())
            if verbose:
                print(f'dateSubList:', dateSubList)
            
            if dateSubList != []:
                dateList = list(dateSubList[0].keys())
                if verbose:
                    print(f'dateList:', dateList)

                dateObjsList = makeDateObj(dateList)
                if verbose:
                    print(f'list of dates converted to timedate objects:\n', dateObjsList)

                #convert dates to days_back and store as dict of case nums
                sched_date_obj = datetime.strptime(key[3], '%Y-%m-%d').date() #convert sched date str to dt
                daysBackDict = makeDaysbackDict(sched_date_obj, dateObjsList, accum_percent_util)
                if verbose:
                    print(f'plottable dictionary:', daysBackDict)

                # refine dict to have no dates older than n days back and tally any previous
                tallyb4window = limitDaysback(daysBackDict, num_lookback_days)
                if verbose:
                    print(f'tallyb4window:', tallyb4window)


                # assemble the dict to plot
                plotDict = assemblePlotDict(emptyDict, daysBackDict, tallyb4window)
                ts_dict[key[3]] = plotDict
                if verbose:
                    print(f'dictionary to plot:', plotDict)

                #put space between loops for troubleshooting    
                if verbose:    
                    print('\n')   
            
    return ts_dict       



##################################################################
#### used for checking plot of specific date - manually ####
##################################################################

#plot data

def plotUtil(x, y, numer1159, denom, sched_date):
    import matplotlib.pyplot as plt #visualizations
    plt.plot(x, y, color="magenta",marker='o',
             markersize=10, LineWidth=4)

    #set y axis to always start at 0
    x1,x2,y1,y2 = plt.axis()  
    plt.axis((x1,x2,0,1.6))

    #rest of plt attributes
    plt.ylabel("% Utilization")
    plt.xlabel("Days Back From Procedure Date")
    plt.axhline(y=1, color='cadetblue', linestyle='--')
    plt.text(-60, .65,
             ('%d' % (numer1159) +' mins\n-------------\n'+ '%d' % (denom) + ' mins'),
             fontsize=15)
    plt.xticks(rotation = 45)
    plt.title('% Utilization of OR vs Days Back\nfrom Procedure Date '+ sched_date)

############################################################################
#### dict with all %util vals per date ready to be averaged and find CI ####
############################################################################

def get_xy_from_ts_dict(ts_dict, agg_dates_to_plot, verbose=False):
    #empty dict to store results
    xy_dict = OrderedDict()
    
    #get x_keys -----------------
    plotDays = list(ts_dict.keys())
    if verbose:
        print(f'plotDays:', plotDays)
    x_pairs = ts_dict[plotDays[0]]
    if verbose:
        print(f'x_pairs:', x_pairs)
    x_keys = list(x_pairs.keys())
    for day_back in x_keys:
        xy_dict[day_back] = [] 
    if verbose:
        print(f'Use days back as x:\n', x_keys)
        print(f'days in xy_dict:', xy_dict)
        print(f'\n--- that was x, now loop y -----\n')
        
        
    #get list of y_vals and store as list in dict
    for date in plotDays:
        if verbose:
            print(f'date:', date)
        y_pairs = ts_dict[date]
        y_values = y_pairs.values()
        if verbose:
            print(f'y_pairs:', y_pairs)
        
        dayback_curr_val_list = []
        #get list of lists of vals
        for day in y_pairs:
            dayback_curr_val_list = xy_dict[day]
            dayback_curr_val_list.append(y_pairs[day])
        if verbose:
            print('\n')
    
    return xy_dict

##################################################################
#### calculate the time series model ####
##################################################################

#calc predictive model from data - mean trendline, CI banding
def calc_ts_model(xy_dict, verbose=False):
    ciList = []
    mnList = []
    
    #iterate through each day and calc avg & sd
    #store them as lists to plot
    
    for i in xy_dict:
        currList = xy_dict[i]
        
        #create center (avg) trendline
        mnList.append(stat.mean(currList))
        
        #calc 1 std
        if len(currList) > 1:
            curr_sd = stat.stdev(currList)
            ciList.append(curr_sd)
            if verbose:
                print(currList)
        else:
            curr_sd = 0
            ciList.append(curr_sd)
            if verbose:
                print(curr_sd)
            

    return mnList, ciList

##################################################################################
##################################################################################
############################## END OF APPENDIX A #################################
##################################################################################
##################################################################################











