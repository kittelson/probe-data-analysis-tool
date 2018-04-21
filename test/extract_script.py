import pandas as pd

tmc = pd.read_csv('C:/Users/ltrask/Downloads/Lexington-Main-St/tmc_identification.csv')
df = pd.read_csv('C:/Users/ltrask/Downloads/Lexington-Main-St/Lexington-Main-St.csv')


tmc_wb = ['125-13038', '125-13037', '125-13036', '125-13035']
tmc_eb = ['125+13036', '125+13037', '125+13038', '125+13039']

tmc_all = ['125-13038', '125-13037', '125-13036', '125-13035', '125+13036', '125+13037', '125+13038', '125+13039']

tmc_wbeb = tmc[tmc['tmc'].isin(tmc_all)]
tmc_wbeb.to_csv('C:/Users/ltrask/Downloads/Lexington-Main-St/tmc_identification_mod.csv')

df_wbeb = df[df['tmc_code'].isin(tmc_all)]
df_wbeb.to_csv('C:/Users/ltrask/Downloads/Lexington-Main-St/Lexington-Main-St_mod.csv')

