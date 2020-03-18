import csv
import datetime
import pandas as pd
import numpy as np
import random
import module_universal as univ

def Sim1(csvRK,csvML,csvML57,csvMRA1,csvSIM1,csvSIM2,csvSIM4):

    col_RK = ['HTSRecTeamScore','TeamID','TeamName','SeriesName','SeriesID','Country','LeagueLevel']
    RK = pd.read_csv(csvRK,usecols=col_RK)
    RK['TeamID']=RK['TeamID'].astype(str)
    HTS_dict = RK.set_index('TeamID')['HTSRecTeamScore'].to_dict()
    TeamName_dict = RK.set_index('TeamID')['TeamName'].to_dict()
    SeriesName_dict = RK.set_index('TeamID')['SeriesName'].to_dict()
    SeriesID_dict = RK.set_index('TeamID')['SeriesID'].to_dict()
    Country_dict = RK.set_index('TeamID')['Country'].to_dict()
    LeagueLevel_dict = RK.set_index('TeamID')['LeagueLevel'].to_dict()

    ##fieldnames = ['TeamID',	'G', 'OG', 'Pts', 'XPts', 'PPts', 'SPts', \
    ##              'SeriesID','TeamName','HTST','SeriesName','Country','LeagueLevel', \
    ##            'P1','P2','P3','P4','P5','P6','P7','P8']

##    fieldnames2 = ['TeamID',	'P1','P2','P3','P4','P5','P6','P7','P8']
##    fieldnames1 = ['TeamID',	'G', 'OG', 'Pts', 'XPts', 'PPts', 'SPts', \
##                  'SeriesID','TeamName','HTST','SeriesName','Country','LeagueLevel']

    ##    'TeamID','P1','P2','P3','P4','P5','P6','P7','P8','SeriesID', 'Country','LeagueLevel', \
    ##              'SPts','SeriesID','TeamName','HTST','SeriesName','G','OG','Pts','XPts','SPts','PPts']


##    with open(csvSIM1,'w',newline='') as csvfile:
##        
##        writer = csv.DictWriter(csvfile, fieldnames1)
##        writer.writeheader()
        
##    with open(csvSIM2,'w',newline='') as csvfile:
##        
##        writer = csv.DictWriter(csvfile, fieldnames2)
##        writer.writeheader()

##    col_MR = ['MatchID','TeamID','Goals','Opp_Goals','HTScore','Opp_HTScore']
    col_MR = ['MatchID','TeamID','Goals','HTScore','Opp_TeamID']    
    MR = pd.read_csv(csvMRA1, usecols = col_MR)
  
    MR['MID_TID'] = MR.MatchID.astype(str) + '_' + MR.TeamID.astype(str)
    MR['Opp_MID_TID'] = MR.MatchID.astype(str) + '_' + MR.Opp_TeamID.astype(str)
    HTS2_dict = MR.set_index('MID_TID')['HTScore']
    Goals_dict = MR.set_index('MID_TID')['Goals']
    MR['Opp_HTScore'] = MR['Opp_MID_TID'].map(HTS2_dict)
    MR['Opp_Goals'] = MR['Opp_MID_TID'].map(Goals_dict)

    MR['HTS_WinProb'] = (pow(MR['HTScore'],3) / (pow(MR['HTScore'],3)+ pow(MR['Opp_HTScore'],3))).round(2)
    MR.loc[((MR.Goals == 5) & (MR.Opp_Goals == 0) & (MR.HTScore == 0)),'HTS_WinProb'] = 1
    MR.loc[((MR.Goals == 0) & (MR.Opp_Goals == 5) & (MR.Opp_HTScore == 0)),'HTS_WinProb'] = 0
        
    MR['WinProb'] = MR['HTS_WinProb'].map(univ.Win_dict)
    MR['DrawProb'] = MR['HTS_WinProb'].map(univ.Draw_dict)
    print('MR',MR[(MR['TeamID']==438624)])
    MR = MR.drop(['MatchID','TeamID','HTS_WinProb','Opp_TeamID'],axis=1)

    ML = pd.read_csv(csvML).append(pd.read_csv(csvML57))

##    ML = ML[ ( ( ML['LeagueID'].isin(['36']) ) & ( ML['LeagueLevel'].isin(['1','2']) ) ) | (ML['LeagueLevelUnitID'].isin(['655','3423']))] #testing

    ML_SL = ML[['LeagueLevelUnitID']]
    ML_SL = ML_SL.drop_duplicates()
    series_list = ML_SL['LeagueLevelUnitID'].map(str).tolist()
    print('series count:',len(series_list))

    ML['MID_TID'] = ML.MatchID.astype(str) + '_' + ML.HomeTeamID.astype(str)
##    print('ML',ML[(ML['HomeTeamID']==438624)])
    ML2 = pd.merge(ML, MR, on='MID_TID', how='left')
    
    ML3 = ML2.dropna()
##    print('ML3',ML3)
    ML3H = ML3[['LeagueLevelUnitID','HomeTeamID','Goals','Opp_Goals','WinProb','DrawProb']].copy()
    ML3H['TeamID'] = ML3H['HomeTeamID'].astype(str)
    ML3H['XPts']=ML3H['WinProb']*3 + ML3H['DrawProb']*1
    ML3H['Pts']=0
    ML3H['G'] = ML3H['Goals']
    ML3H['OG'] = ML3H['Opp_Goals']

    ML3H.loc[(ML3H.G > ML3H.OG),'Pts'] = 3
    ML3H.loc[(ML3H.G == ML3H.OG),'Pts'] = 1

    ML3A = ML3[['LeagueLevelUnitID','AwayTeamID','Goals','Opp_Goals','WinProb','DrawProb']].copy()
    ML3A['TeamID'] = ML3A['AwayTeamID'].astype(str)
    ML3A['XPts']=(1-ML3A['WinProb']-ML3A['DrawProb'])*3 + ML3A['DrawProb']*1
    ML3A['Pts']=0
    ML3A['G'] = ML3A['Opp_Goals']
    ML3A['OG'] = ML3A['Goals']

    ML3A.loc[(ML3A.G > ML3A.OG),'Pts'] = 3
    ML3A.loc[(ML3A.G == ML3A.OG),'Pts'] = 1


    ML3X = pd.concat([ML3H,ML3A],sort=True) # True means it reorders the columns
    ML3Y = ML3X.groupby('TeamID')['G','OG','Pts','XPts'].sum().reset_index().copy()
    ML3Y['XPts'] = ML3Y['XPts'].round(1)
    Pts_dict = ML3Y.set_index('TeamID')['Pts'].to_dict()

    format_cols = ['G', 'OG']
    ML3Y[format_cols] = ML3Y[format_cols].applymap(np.int64)

    ML4 = ML2[ML2.isnull().any(1)] # these are matches that haven't happened yet 
    ML4 = ML4[['LeagueLevelUnitID','HomeTeamID','AwayTeamID','MatchRound']]
    ML4['LeagueLevelUnitID'] = ML4['LeagueLevelUnitID'].astype(str)
    SeriesMinRound_dict = ML4.groupby('LeagueLevelUnitID')['MatchRound'].min().round(0)
    
##    SeriesMinRound_dict.to_csv('zML4Z_SMR.csv',mode='w', header= True,index=True)

    ML4['MSID_TeamH'] = ML4.HomeTeamID.astype(str)
    ML4['MSID_TeamA'] = ML4.AwayTeamID.astype(str)

    ML4['TeamH_HTS'] = ML4['HomeTeamID'].astype(str).map(HTS_dict) / univ.loc_dict.get('H')
    ML4['TeamA_HTS'] = ML4['AwayTeamID'].astype(str).map(HTS_dict) / univ.loc_dict.get('A')

    ML4['TeamH_HTS'] = ML4['TeamH_HTS'].fillna(0.1)
    ML4['TeamA_HTS'] = ML4['TeamA_HTS'].fillna(0.1)

    ML4['HTS_WinProb'] = (pow(ML4['TeamH_HTS'],3) / (pow(ML4['TeamH_HTS'],3)+ pow(ML4['TeamA_HTS'],3))).round(2)
    ML4['WinP'] = ML4['HTS_WinProb'].map(univ.Win_dict) * 100
    ML4['DrawP'] = ML4['HTS_WinProb'].map(univ.Draw_dict) * 100
##    print('ML4', ML4[['HomeTeamID','TeamH_HTS','TeamA_HTS']]) #testing
##    print('ML4', ML4[['HomeTeamID','WinP','DrawP']]) #testing
    
    ML4H = ML4[['HomeTeamID','WinP','DrawP','MatchRound','AwayTeamID','LeagueLevelUnitID']].copy()
    ML4H['TeamID']=ML4H['HomeTeamID'].astype(str)
    ML4H['Opp_TeamID']=ML4H['AwayTeamID'].astype(str)
    ML4H['PPtsH']=ML4H['WinP']*.03 + ML4H['DrawP']*.01
    ML4H['Loc']='H'
##    print('ML4H',ML4H) #testing
    ML4A = ML4[['AwayTeamID','WinP','DrawP','MatchRound','HomeTeamID','LeagueLevelUnitID']].copy()
    ML4A['TeamID']=ML4A['AwayTeamID'].astype(str)
    ML4A['Opp_TeamID']=ML4A['HomeTeamID'].astype(str)
    ML4A['PPtsA']=(100-ML4A['WinP']-ML4A['DrawP'])*.03 + ML4A['DrawP']*.01
    ML4A['Loc']='A'
##    print('ML4A',ML4A) #testing

    MS_col = ['LeagueLevelUnitID','MSID_TeamH','MSID_TeamA','WinP','DrawP']
    ML5 = ML4[MS_col].copy()
##    print('ML5',ML5)
    ML5.to_csv(csvSIM4, mode='w', header= True,index=False)

    PPtsH_dict = ML4H.groupby('TeamID')['PPtsH'].sum().round(1)
    PPtsA_dict = ML4A.groupby('TeamID')['PPtsA'].sum().round(1)
        

    ML4Z = pd.concat([ML4H,ML4A],sort=True)
##    ML4Z.to_csv('zML4Z.csv',mode='w', header= True,index=False)
    print(ML4Z[0:15])
    ML4Z['NextRound'] = ML4Z['LeagueLevelUnitID'].map(SeriesMinRound_dict)
    ML4Z = ML4Z[(ML4Z['NextRound']==ML4Z['MatchRound'])]
    NextOpp_dict = ML4Z.set_index('TeamID')['Opp_TeamID'].to_dict()
    NextWinP_dict = ML4Z.set_index('TeamID')['WinP'].to_dict()
    NextDrawP_dict = ML4Z.set_index('TeamID')['DrawP'].to_dict()
    Loc_dict = ML4Z.set_index('TeamID')['Loc'].to_dict()
    
    
    ML3Y['TeamID'] = ML3Y['TeamID'].astype(str)
    ML3Y['PPts'] = ML3Y['TeamID'].map(PPtsH_dict).fillna(0) + ML3Y['TeamID'].map(PPtsA_dict).fillna(0)
    ML3Y['SPts'] = ML3Y['Pts']+ML3Y['PPts']

    ML3Y['SeriesID']=ML3Y['TeamID'].map(SeriesID_dict)
    ML3Y['TeamName']=ML3Y['TeamID'].map(TeamName_dict)
    ML3Y['HTST']=ML3Y['TeamID'].map(HTS_dict)
    ML3Y['SeriesName']=ML3Y['TeamID'].map(SeriesName_dict)
    ML3Y['Country']=ML3Y['TeamID'].map(Country_dict)
    ML3Y['LeagueLevel']=ML3Y['TeamID'].map(LeagueLevel_dict)
##    print(ML3Y[['TeamID','SeriesID','SPts','PPts']])
    ML3Y['NextOppID'] = ML3Y['TeamID'].map(NextOpp_dict)
    ML3Y['NextDrawP'] = ML3Y['TeamID'].map(NextDrawP_dict)
    ML3Y['NextWinP'] = ML3Y['TeamID'].map(NextWinP_dict)
    ML3Y['NextLoc'] = ML3Y['TeamID'].map(Loc_dict)
    ML3Y.loc[(ML3Y.NextLoc == 'A'),'NextWinP'] = 100-ML3Y['TeamID'].map(NextWinP_dict)-ML3Y['NextDrawP']
##    ML3A.loc[(ML3A.G == ML3A.OG),'Pts'] = 1
    ML3Y['NextOppName'] = ML3Y['NextOppID'].map(TeamName_dict)
    
##    print(SeriesMinRound_dict)
##    print(SeriesMinRound_dict['655'])
    ML3Y['NextRound'] = ML3Y['SeriesID'].astype(str).map(SeriesMinRound_dict)
##    ML3Y = ML3Y.drop(['NextWinPA'],axis=1)
    ML3Y.to_csv(csvSIM1, mode='w', header= True,index=False)


    ## ## now adding in the "next season" part 
def Sim2(csvSIM1,csvSIM2,csvSIM3,csvSIM4,csvML,sims,wk):   

    csv_MS_col = ['MSID_TeamH','MSID_TeamA','WinP','DrawP']
    csv_MS3_col = csv_MS_col + ['simul']
    choicesH = [3,1,0]
    choicesA = [0,1,3]
    csv_MS4_col = ['Series_simul','Team_simul','TeamHTS','Pts']
    csv_SC6_col = ['TeamID','P1','P2','P3','P4','P5','P6','P7','P8']
    csv_SC6 = pd.DataFrame(columns=csv_SC6_col)

##    col_SIM1 = ['HTST','TeamID','Pts']
    SIM1 = pd.read_csv(csvSIM1)
    SIM1['TeamID']=SIM1['TeamID'].astype(str)
    SIM1['SeriesID']=SIM1['SeriesID'].astype(str)
    HTS_dict = SIM1.set_index('TeamID')['HTST'].to_dict()
    Pts_dict = SIM1.set_index('TeamID')['Pts'].to_dict()
        
    ML_SL = pd.read_csv(csvML,usecols=['LeagueLevelUnitID','HomeTeamID']).drop_duplicates()
##    ML_SL = ML[['LeagueLevelUnitID']]
##    ML_SL = ML_SL.drop_duplicates()
    Team_Series_map = ML_SL.set_index('HomeTeamID')['LeagueLevelUnitID'].to_dict()
    ML_SL = ML_SL[['LeagueLevelUnitID']].drop_duplicates()
    series_list1 = ML_SL['LeagueLevelUnitID'].map(str).tolist()
    print('series count:',len(series_list1))
   
    
    SA = pd.read_csv(csvSIM2,usecols=['TeamID'])
    SA['LeagueLevelUnitID'] = SA['TeamID'].map(Team_Series_map)
##    SA = SA[['LeagueLevelUnitID']].drop_duplicates()    
    Series_Already_list = SA['LeagueLevelUnitID'].map(str).to_list()

    series_list = list(set(series_list1) - set(Series_Already_list))  # removes the ones already processed
    print('series count after Series Already: ', len(series_list))

    ML6A = pd.read_csv(csvSIM4)
    
##    series_list = ['3423']
    print('before', datetime.datetime.now())
    for SeriesID in series_list:
        
    ##    csv_MS = pd.DataFrame(columns=csv_MS_col) # create again as blank
        csv_MS = ML6A[(ML6A['LeagueLevelUnitID'].map(str)==SeriesID)].copy()
        
    ##    print('csv_MS: ', csv_MS)
        csv_MS3 = pd.DataFrame(columns=csv_MS3_col)
    ##    csv_MS4 = csv_MS[['MSID_TeamH']].drop_duplicates()
    ##    print('csv_MS4: ',csv_MS4)
        for i in range(sims):
    ##        print('sim i',i + 1)
            csv_MS['simul'] = i + 1
    ##        csv_MS3 = csv_MS3.append(csv_MS[csv_MS3_col])
            csv_MS3 = csv_MS3.append(csv_MS)

    ##        print('csv_MS3: ',csv_MS3)

            csv_MS3['randResult'] = [ random.randint(0,100)  for k in csv_MS3.index]
            conditions = [
                (csv_MS3['randResult']<=csv_MS3['WinP']),
                (csv_MS3['randResult']>csv_MS3['WinP']) & ( csv_MS3['randResult']<=csv_MS3['DrawP'] ),
                (csv_MS3['randResult']>csv_MS3['DrawP'])
                ]        

            csv_MS3['MatchOutcomeH'] = np.select(conditions,choicesH,default=9)
            csv_MS3['MatchOutcomeA'] = np.select(conditions,choicesA,default=9)
            csv_MS3['TeamH_simul'] = csv_MS3['MSID_TeamH'].map(str) + '_' + csv_MS3['simul'].map(str)
            csv_MS3['TeamA_simul'] = csv_MS3['MSID_TeamA'].map(str) + '_' + csv_MS3['simul'].map(str)
####            csv_MS3.to_csv('zsim.csv', mode='w', header= True,index=False)  #testing
    

            if i+1 == sims:
    ##            print('csv_MS3: ',csv_MS3)
                PtsH_dict = csv_MS3.groupby('TeamH_simul')['MatchOutcomeH'].sum()
                PtsA_dict = csv_MS3.groupby('TeamA_simul')['MatchOutcomeA'].sum()
                csv_MS4 = pd.DataFrame(columns=csv_MS4_col)

                csv_MS4['Team_simul'] = csv_MS3['TeamH_simul'].append(csv_MS3['TeamA_simul']).drop_duplicates()
                                
                csv_MS4['TeamID'] = csv_MS4['Team_simul'].str.split('_').str[0]
                csv_MS4['TeamHTS'] = csv_MS4['TeamID'].astype(str).map(HTS_dict) 
    ##            csv_MS4['Series_simul'] = csv_MS4['Team_simul'].str.split('_').str[0] + '_' + csv_MS4['Team_simul'].str.split('_').str[2]
                csv_MS4['Series_simul'] = csv_MS4['Team_simul'].str.split('_').str[1]
            
                csv_MS4['PtsTD'] = csv_MS4['TeamID'].map(Pts_dict)
                csv_MS4['PtsH'] = csv_MS4['Team_simul'].map(PtsH_dict).fillna(0)
                csv_MS4['PtsA'] = csv_MS4['Team_simul'].map(PtsA_dict).fillna(0)
    ##        print(csv_MS3)
                csv_MS4['Pts'] = csv_MS4['Team_simul'].map(PtsH_dict).fillna(0) + csv_MS4['Team_simul'].map(PtsA_dict).fillna(0) + csv_MS4['TeamID'].map(Pts_dict)
                csv_MS4 = csv_MS4.sort_values(['Series_simul','Pts','TeamHTS'],ascending=[True,False,False])
                csv_MS4['Pos'] = csv_MS4['Series_simul'].groupby((csv_MS4['Series_simul'] != csv_MS4['Series_simul'].shift()).cumsum()).cumcount() + 1
##                print('MS4',csv_MS4)
    ##        if i+1 == sims:
                csv_SC4 = csv_MS4.groupby(['TeamID','Pos']).size().reset_index(name='count')
                csv_SC4['Position'] = 'P' + csv_SC4['Pos'].map(str)
    ##        
    ##        
                csv_SC5 = csv_SC4.pivot(index='TeamID',columns='Position',values='count')
                csv_SC5 = csv_SC5.div(sims)
                
    ##        ##        csv_SC6 = csv_SC6.append(csv_SC5)
    ##            print('csv_SC5:', csv_SC5)
                csv_SC5.to_csv(csvSIM2, mode='a', header= False)
                print('end series_', SeriesID, '_', datetime.datetime.now())
    ##
    print('pre merge',datetime.datetime.now())

    
    SC6 = pd.read_csv(csvSIM2)

    SC6['TeamID'] = SC6['TeamID'].map(str)
    SIM1 = SIM1[(SIM1['SeriesID'].isin(series_list1))]
    ML6 = pd.merge(SIM1,SC6,on='TeamID',how='left')

    ML6.to_csv(csvSIM3, mode='w', header= True,index=False)
    now = datetime.datetime.now()  
    print('end', now)
