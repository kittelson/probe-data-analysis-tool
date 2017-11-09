import os
import datetime

os.chdir('C:/Users/ltrask/Documents/21383 - NCDOT SPM/Dat')
files = os.listdir()

d1 = datetime.datetime(2037, 4, 29)
d2 = datetime.datetime(2017, 10, 2)
delta = d1 - d2

for f_name in files:
    in_dat = open(f_name, 'rb')
    tokens = f_name.split('_')
    old_date_dt = datetime.datetime(int(tokens[2]), int(tokens[3]), int(tokens[4]))
    old_date_str1 = '{d.month}-{d.day}-{d.year}'.format(d=old_date_dt)
    old_date1 = bytes(old_date_str1, 'utf8')
    old_date_str2 = old_date_dt.strftime('%Y_%m_%d')
    old_date2 = bytes(old_date_str2, 'utf8')
    old_date_str3 = '{d.month}/{d.day}/{d.year}'.format(d=old_date_dt)
    old_date3 = bytes(old_date_str3, 'utf8')
    new_date_dt = old_date_dt - delta
    new_date_str1 = '{d.month}-{d.day}-{d.year}'.format(d=new_date_dt)
    new_date1 = bytes(new_date_str1, 'utf8')
    new_date_str2 = new_date_dt.strftime('%Y_%m_%d')
    new_date2 = bytes(new_date_str2, 'utf8')
    new_date_str3 = '{d.month}/{d.day}/{d.year}'.format(d=new_date_dt)
    new_date3 = bytes(new_date_str3, 'utf8')

    out_dat = open(f_name.replace(old_date_str2, new_date_str2), 'wb')
    for line in in_dat:
        out_dat.write(line.replace(old_date1, new_date1).replace(old_date2,new_date2).replace(old_date3, new_date3))
    in_dat.close()
    out_dat.close()


# f = open('C:/Users/ltrask/Documents/21383 - NCDOT SPM/Dat/ECON_10.10.1.11_2037_04_29_1415.dat', 'rb')
# line_idx = 0
# while line_idx < 6:
#     print(f.readline())
#     line_idx += 1
# f.close()
#
# f = open('C:/Users/ltrask/Documents/21383 - NCDOT SPM/Dat/ECON_10.10.1.11_2037_04_29_1415_fix.dat', 'rb')
# line_idx = 0
# while line_idx < 6:
#     print(f.readline())
#     line_idx += 1
# f.close()