import pandas as pd
from data_import import get_speed_contour_cs


fname, tmc, site_name, start_date, od1, od2, end_date = get_speed_contour_cs(1)

df = pd.read_csv(fname)
