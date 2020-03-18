import pandas as pd

csvPredHTM = 'PredHTM_R04.csv'
csvWin = 'htm_win.csv'

csvPredHTM2 = 'PredHTM_R04v2.csv'

htm = pd.read_csv(csvPredHTM)
Win = pd.read_csv(csvWin)

Win_dict = Win.set_index('TeamID')['Win'].to_dict()
htm['WinCup']=htm['TeamID'].map(Win_dict)
htm.to_csv(csvPredHTM2,mode='w',index=False)      
