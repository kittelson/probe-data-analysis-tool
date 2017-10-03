import datetime
import pandas as pd


def create_casestudy(cs_idx):
    if cs_idx == 1:
        site_name = 'I-66 EB Weekend'
        fname = 'C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/I66_Wknd_EB_20140916_20170131/I66_Wknd_EB_20140916_20170131.csv'
        start_date = datetime.date(2014, 9, 16)
        open_date1 = datetime.date(2015, 9, 16)
        open_date2 = datetime.date(2016, 3, 31)
        end_date = datetime.date(2017, 1, 31)
        tmc = extract_tmc('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/I66_Wknd_EB_20140916_20170131/TMC_Identification.csv')

    elif cs_idx == 2:
        site_name = 'I-66 WB Weekend'
        fname = 'C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/I66_Wknd_WB_20140916_20170131/I66_Wknd_WB_20140916_20170131.csv'
        start_date = datetime.date(2014, 9, 16)
        open_date1 = datetime.date(2015, 9, 16)
        open_date2 = datetime.date(2016, 3, 31)
        end_date = datetime.date(2017, 1, 31)
        tmc = extract_tmc('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/I66_Wknd_WB_20140916_20170131/TMC_Identification.csv')
    elif cs_idx == 3:
        site_name = 'I-70 EB Sunday'
        fname = 'C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/I70_CO_EB_20141212_20170131/I70_CO_EB_20141212_20170131.csv'
        start_date = datetime.date(2014, 12, 12)
        open_date1 = datetime.date(2015, 12, 11)
        open_date2 = datetime.date(2015, 12, 12)
        end_date = datetime.date(2017, 1, 31)
        tmc = extract_tmc('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/I70_CO_EB_20141212_20170131/TMC_Identification.csv')
    elif cs_idx == 4:
        site_name = 'I-78 EB Weekday AM Peak'
        fname = 'C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/I78_NJ_EB_20130331_20170131/I78_NJ_EB_20130331_20170131.csv'
        start_date = datetime.date(2013, 3, 31)
        open_date1 = datetime.date(2014, 3, 31)
        open_date2 = datetime.date(2015, 3, 31)
        end_date = datetime.date(2017, 1, 31)
        tmc = extract_tmc('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/I78_NJ_EB_20130331_20170131/TMC_Identification.csv')
    elif cs_idx == 5:
        site_name = 'I-495 NB Weekday'
        fname = 'C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/I495_Wkdy_NB_20130707_20170131/I495_Wkdy_NB_20130707_20170131.csv'
        start_date = datetime.date(2013, 7, 7)
        open_date1 = datetime.date(2014, 7, 7)
        open_date2 = datetime.date(2015, 7, 7)
        end_date = datetime.date(2017, 1, 31)
        tmc = extract_tmc('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/I495_Wkdy_NB_20130707_20170131/TMC_Identification.csv')
    elif cs_idx == 6:
        site_name = 'TX-161 NB Weekday'
        fname = 'C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/TX161_Wkdy_NB_20140914_20170131/TX161_Wkdy_NB_20140914_20170131.csv'
        start_date = datetime.date(2014, 9, 14)
        open_date1 = datetime.date(2015, 9, 13)
        open_date2 = datetime.date(2015, 9, 14)
        end_date = datetime.date(2017, 1, 31)
        tmc = extract_tmc('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/TX161_Wkdy_NB_20140914_20170131/TMC_Identification.csv')
    elif cs_idx == 7:
        site_name = 'TX-161 SB Weekday'
        fname = 'C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/TX161_Wkdy_SB_20140914_20170131/TX161_Wkdy_SB_20140914_20170131.csv'
        start_date = datetime.date(2014, 9, 14)
        open_date1 = datetime.date(2015, 9, 13)
        open_date2 = datetime.date(2015, 9, 14)
        end_date = datetime.date(2017, 1, 31)
        tmc = extract_tmc('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/TX161_Wkdy_SB_20140914_20170131/TMC_Identification.csv')
    elif cs_idx == 8:
        site_name = 'I-66 EB Weekday'
        fname = 'C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/I66_Wkdy_EB_20140916_20170131/I66_Wkdy_EB_20140916_20170131.csv'
        start_date = datetime.date(2014, 9, 16)
        open_date1 = datetime.date(2015, 9, 16)
        open_date2 = datetime.date(2016, 3, 31)
        end_date = datetime.date(2017, 1, 31)
        tmc = extract_tmc('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/I66_Wkdy_EB_20140916_20170131/TMC_Identification.csv')
    elif cs_idx == 9:
        site_name = 'I-66 WB Weekday'
        fname = 'C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/I66_Wkdy_WB_20140916_20170131/I66_Wkdy_WB_20140916_20170131.csv'
        start_date = datetime.date(2014, 9, 16)
        open_date1 = datetime.date(2015, 9, 16)
        open_date2 = datetime.date(2016, 3, 31)
        end_date = datetime.date(2017, 1, 31)
        tmc = extract_tmc('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/I66_Wkdy_WB_20140916_20170131/TMC_Identification.csv')
    elif cs_idx == 10:
        site_name = 'I-66 EB Weekday - Full Extent'
        fname = 'C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/I66_EB_20140916_20170131_Updated/I66_EB_20140916_20170131_Updated.csv'
        start_date = datetime.date(2014, 9, 16)
        open_date1 = datetime.date(2015, 9, 16)
        open_date2 = datetime.date(2016, 3, 31)
        end_date = datetime.date(2017, 1, 31)
        tmc = extract_tmc('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/I66_EB_20140916_20170131_Updated/TMC_Identification.csv')
    elif cs_idx == 11:
        site_name = 'I-66 EB Weekend - Full Extent'
        fname = 'C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/I66_EB_FullExtent_Wknd_20140916_20170131/I66_EB_FullExtent_Wknd_20140916_20170131.csv'
        start_date = datetime.date(2014, 9, 16)
        open_date1 = datetime.date(2015, 9, 16)
        open_date2 = datetime.date(2016, 3, 31)
        end_date = datetime.date(2017, 1, 31)
        tmc = extract_tmc('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/I66_EB_FullExtent_Wknd_20140916_20170131/TMC_Identification.csv')
    elif cs_idx == 12:
        site_name = 'I-66 WB All Days - Full Extent'
        fname = 'C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/I66_WB_Full_20140916_20170131/I66_WB_Full_20140916_20170131.csv'
        start_date = datetime.date(2014, 9, 16)
        open_date1 = datetime.date(2015, 9, 16)
        open_date2 = datetime.date(2016, 3, 31)
        end_date = datetime.date(2017, 1, 31)
        tmc = extract_tmc('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/I66_WB_Full_20140916_20170131/TMC_Identification.csv')
    else:
        site_name = 'I-66 EB Weekday - 6 Mile Dynamic Shoulder'
        fname = 'C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/I66_EB_20140916_20170131_DSU/I66_EB_20140916_20170131_DSU.csv'
        start_date = datetime.date(2014, 9, 16)
        open_date1 = datetime.date(2015, 9, 16)
        open_date2 = datetime.date(2016, 3, 31)
        end_date = datetime.date(2017, 1, 31)
        tmc = extract_tmc('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/I66_EB_20140916_20170131_DSU/TMC_Identification.csv')

    return fname, tmc, site_name, start_date, open_date1, open_date2, end_date


def create_case_study2(cs_idx):
    if cs_idx == 1:
        site_name = 'I-66 Eastbound'
        fname = 'C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/I66_EB_20140916_20170131_Updated/I66_EB_20140916_20170131_Updated.csv'
        start_date = datetime.date(2014, 9, 16)
        open_date1 = datetime.date(2015, 9, 16)
        open_date2 = datetime.date(2016, 3, 31)
        end_date = datetime.date(2017, 1, 31)
        tmc = extract_tmc('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/I66_EB_20140916_20170131_Updated/TMC_Identification.csv')
    elif cs_idx == 2:
        site_name = 'I-66 Eastbound'
        fname = 'C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/I66_EB_FullExtent_Wknd_20140916_20170131/I66_EB_FullExtent_Wknd_20140916_20170131.csv'
        start_date = datetime.date(2014, 9, 16)
        open_date1 = datetime.date(2015, 9, 16)
        open_date2 = datetime.date(2016, 3, 31)
        end_date = datetime.date(2017, 1, 31)
        tmc = extract_tmc('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/I66_EB_FullExtent_Wknd_20140916_20170131/TMC_Identification.csv')
    elif cs_idx == 3:
        site_name = 'I-66 Westbound'
        fname = 'C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/I66_WB_Full_20140916_20170131/I66_WB_Full_20140916_20170131.csv'
        start_date = datetime.date(2014, 9, 16)
        open_date1 = datetime.date(2015, 9, 16)
        open_date2 = datetime.date(2016, 3, 31)
        end_date = datetime.date(2017, 1, 31)
        tmc = extract_tmc('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/I66_WB_Full_20140916_20170131/TMC_Identification.csv')
    elif cs_idx == 4:
        site_name = 'I-70 Eastbound'
        fname = 'C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/I70_CO_EB_Extended_20141201_20170131/I70_CO_EB_Extended_20141201_20170131.csv'
        start_date = datetime.date(2014, 12, 1)
        open_date1 = datetime.date(2015, 12, 11)
        open_date2 = datetime.date(2015, 12, 12)
        end_date = datetime.date(2017, 1, 31)
        tmc = extract_tmc('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/I70_CO_EB_Extended_20141201_20170131/TMC_Identification.csv')
    elif cs_idx == 5:
        site_name = 'I-78 Eastbound'
        fname = 'C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/I78_NJ_EB_Extended_20130301_20170131/I78_NJ_EB_Extended_20130301_20170131.csv'
        start_date = datetime.date(2013, 3, 1)
        open_date1 = datetime.date(2014, 3, 31)
        open_date2 = datetime.date(2015, 3, 31)
        end_date = datetime.date(2017, 1, 31)
        tmc = extract_tmc('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/I78_NJ_EB_Extended_20130301_20170131/TMC_Identification.csv')
    elif cs_idx == 6:
        site_name = 'I-495 Northbound (7 mi)'
        fname = 'C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/I495_VA_NB_Extended_20130701_20170131/I495_VA_NB_Extended_20130701_20170131.csv'
        start_date = datetime.date(2013, 7, 1)
        open_date1 = datetime.date(2014, 7, 7)
        open_date2 = datetime.date(2015, 7, 7)
        end_date = datetime.date(2017, 1, 31)
        tmc = extract_tmc('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/I495_VA_NB_Extended_20130701_20170131/TMC_Identification.csv')
    elif cs_idx == 7:
        site_name = 'I-495 Northbound (13 mi)'
        fname = 'C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/I495_VA_NB_Ext13Mi_20130701_20170131/I495_VA_NB_Ext13Mi_20130701_20170131.csv'
        start_date = datetime.date(2013, 7, 1)
        open_date1 = datetime.date(2014, 7, 7)
        open_date2 = datetime.date(2015, 7, 7)
        end_date = datetime.date(2017, 1, 31)
        tmc = extract_tmc('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/I495_VA_NB_Ext13Mi_20130701_20170131/TMC_Identification.csv')
    elif cs_idx == 8:
        site_name = 'TX-161 Northbound'
        fname = 'C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/TX161_TX_NB_Extended_20140901_20170131/TX161_TX_NB_Extended_20140901_20170131.csv'
        start_date = datetime.date(2014, 9, 1)
        open_date1 = datetime.date(2015, 9, 13)
        open_date2 = datetime.date(2015, 9, 14)
        end_date = datetime.date(2017, 1, 31)
        tmc = extract_tmc('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/TX161_TX_NB_Extended_20140901_20170131/TMC_Identification.csv')
    elif cs_idx == 9:
        site_name = 'TX-161 Southbound'
        fname = 'C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/TX161_TX_SB_Extended_20140901_20170131/TX161_TX_SB_Extended_20140901_20170131.csv'
        start_date = datetime.date(2014, 9, 1)
        open_date1 = datetime.date(2015, 9, 13)
        open_date2 = datetime.date(2015, 9, 14)
        end_date = datetime.date(2017, 1, 31)
        tmc = extract_tmc('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/TX161_TX_SB_Extended_20140901_20170131/TMC_Identification.csv')
    elif cs_idx == 10:
        site_name = 'AK Way Viad Northbound'
        fname = 'C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/AlaskanWayVia_NB_20140101_20170131/AlaskanWayVia_NB_20140101_20170131.csv'
        start_date = datetime.date(2015, 1, 1)
        open_date1 = datetime.date(2015, 12, 31)
        open_date2 = datetime.date(2016, 1, 1)
        end_date = datetime.date(2016, 12, 31)
        tmc = extract_tmc('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/AlaskanWayVia_NB_20140101_20170131/TMC_Identification.csv')
    else:
        site_name = 'AK Way Viad Southbound'
        fname = 'C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/AlaskanWayVia_SB_20140101_20170131/AlaskanWayVia_SB_20140101_20170131.csv'
        start_date = datetime.date(2015, 1, 1)
        open_date1 = datetime.date(2015, 12, 31)
        open_date2 = datetime.date(2016, 1, 1)
        end_date = datetime.date(2016, 12, 31)
        tmc = extract_tmc('C:/Users/ltrask/Documents/18112 - FHWA Shoulder Use/Ext/AlaskanWayVia_SB_20140101_20170131/TMC_Identification.csv')

    return fname, tmc, site_name, start_date, open_date1, open_date2, end_date


def get_speed_contour_cs(cs_idx):
    if cs_idx == 1:
        site_name = 'I-4 BtU North Section'
        fname = 'C:/Users/ltrask/Documents/13066 - I4 BtU/VISSIM/I4_NorthSection_2016_AllDays/I4_NorthSection_2016_AllDays.csv'
        start_date = datetime.date(2014, 9, 1)
        open_date1 = datetime.date(2015, 9, 13)
        open_date2 = datetime.date(2015, 9, 14)
        end_date = datetime.date(2017, 1, 31)
        tmc = extract_tmc('C:/Users/ltrask/Documents/13066 - I4 BtU/VISSIM/I4_NorthSection_2016_AllDays/TMC_Identification.csv')
    return fname, tmc, site_name, start_date, open_date1, open_date2, end_date

def get_spm_case_study(cs_idx):
    path = 'C:/Users/ltrask/Documents/21383 - NCDOT SPM/CaseStudies/'
    path1 = 'Site'
    path2 = '_20140301_20170930'
    # path2 = '_NPMRDS_20140301_20170131'
    tmc_path = 'TMC_Identification.csv'
    data_path = path1 + str(cs_idx) + path2 + '.csv'
    site_name = 'Site ' + str(cs_idx)
    fname = path + path1 + str(cs_idx) + path2 + '/' + data_path
    start_date = datetime.date(2015, 12, 1)
    open_date1 = datetime.date(2016, 12, 31)
    open_date2 = datetime.date(2017, 1, 1)
    end_date = datetime.date(2017, 8, 30)
    tmc = extract_tmc(path + path1 + str(cs_idx) + path2 + '/' + tmc_path)
    dirs = tmc['direction'].unique()
    tmc_subset1 = tmc[tmc['direction'] == dirs[0]]['tmc']
    return fname, tmc, site_name, start_date, open_date1, open_date2, end_date


def get_spm_study_list():
    l = ('Site 1', 'Site 2', 'Site 3', 'Site 4', 'Site 5')
    return l


def get_case_study_list():
    l = ("I-66 EB Weekday",
         "I-66 EB Weekend",
         "I-66 WB All Days",
         "I-70 EB All Days",
         "I-78 EB All Days",
         "I-495 (7mi) NB All Days",
         "I-495 (13mi) NB All Days",
         "TX-161 NB All Days",
         "TX-161 SB All Days",
         "AK Way Viad NB",
         "AK Way Viad SB")
    return l

def extract_tmc(fname):
    tmc = pd.read_csv(fname)
    tmc.set_index(tmc['tmc'], inplace=True)
    return tmc
