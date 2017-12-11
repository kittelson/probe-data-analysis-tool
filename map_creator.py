
MK_STR1 = 'var marker_{} = L.marker('
MK_STR15 = '[33.96012,-77.93851],\n'
MK_STR2 = '{\nicon: new L.Icon.Default()\n}\n).addTo(map_facility);\n'

MK_PU_STR1_1 = 'var popup_{}'
MK_PU_STR1_2 = ' = L.popup({maxWidth: \'300\'});\n'
MK_PU_STR2 = 'var html_{} = $(\'<div id="html_{}" style="width: 100.0%; height: 100.0%;">{}</div>\')[0];\n'
MK_PU_STR3 = 'popup_{}.setContent(html_{});\n'
MK_PU_STR4 = 'marker_{}.bindPopup(popup_{});\n'


PL_STR1 = 'var poly_line_{} = L.polyline('
PL_STR15 = '[[33.96012,-77.93851], [33.96094,-77.93511]]'
PL_STR2 = ',\n{\n"bubblingMouseEvents": true,\n"color": "black",\n"dashArray": null,\n "dashOffset": null,\n"fill": false,\n"fillColor": "black",\n  "fillOpacity": 0.2,\n"fillRule": "evenodd",\n"lineCap": "round",\n"lineJoin": "round", \n"noClip": false,\n"opacity": 1.0, \n"smoothFactor": 1.0,\n"stroke": true, \n"weight": 3\n}).addTo(map_facility);\n'

PL_HL_OVER_STR1 = 'poly_line_{}'
PL_HL_OVER_STR1_1 = '.on(\'mouseover\', function(e) {\n'
PL_HL_OVER_STR2 = 'var layer = e.target;\n'
PL_HL_OVER_STR3 = 'layer.setStyle({\n'
PL_HL_OVER_STR4 = 'color: \'blue\',\n'
PL_HL_OVER_STR5 = 'opacity: 1,\n'
PL_HL_OVER_STR6 = 'weight: 5\n'
PL_HL_OVER_STR7 = '});\n'
PL_HL_OVER_STR8 = '});\n'

PL_HL_OUT_STR1 = 'poly_line_{}'
PL_HL_OUT_STR1_1 = '.on(\'mouseout\', function(e) {\n'
PL_HL_OUT_STR2 = 'var layer = e.target;\n'
PL_HL_OUT_STR3 = 'layer.setStyle({\n'
PL_HL_OUT_STR4 = 'color: \'black\',\n'
PL_HL_OUT_STR5 = 'opacity: 1,\n'
PL_HL_OUT_STR6 = 'weight: 3\n'
PL_HL_OUT_STR7 = '});\n'
PL_HL_OUT_STR8 = '});\n'

END_STR = '</script>'


def create_html_map(tmc_list):
    f_base = open('static/base_map.txt', 'r')
    base_str = ''
    for line in f_base:
        base_str = base_str + line
    f_new = open('templates/test_map.html', 'w')
    f_new.write(base_str)
    for index, tmc in tmc_list.iterrows():
        idx_str = str(index)
        lat_lon_arr = [tmc['start_latitude'], tmc['start_longitude']]
        route_arr = [[tmc['start_latitude'], tmc['start_longitude']], [tmc['end_latitude'], tmc['end_longitude']]]
        f_new.write(MK_STR1.format(idx_str))
        f_new.write(str(lat_lon_arr) + ',\n')
        f_new.write(MK_STR2)
        f_new.write(MK_PU_STR1_1.format(idx_str))
        f_new.write(MK_PU_STR1_2)
        f_new.write(MK_PU_STR2.format(idx_str, idx_str, idx_str))
        f_new.write(MK_PU_STR3.format(idx_str, idx_str))
        f_new.write(MK_PU_STR4.format(idx_str, idx_str))
        f_new.write(PL_STR1.format(idx_str))
        f_new.write(str(route_arr))
        f_new.write(PL_STR2)
        f_new.write(PL_HL_OVER_STR1.format(idx_str))
        f_new.write(PL_HL_OVER_STR1_1)
        f_new.write(PL_HL_OVER_STR2)
        f_new.write(PL_HL_OVER_STR3)
        f_new.write(PL_HL_OVER_STR4)
        f_new.write(PL_HL_OVER_STR5)
        f_new.write(PL_HL_OVER_STR6)
        f_new.write(PL_HL_OVER_STR7)
        f_new.write(PL_HL_OVER_STR8)
        f_new.write(PL_HL_OUT_STR1.format(idx_str))
        f_new.write(PL_HL_OUT_STR1_1)
        f_new.write(PL_HL_OUT_STR2)
        f_new.write(PL_HL_OUT_STR3)
        f_new.write(PL_HL_OUT_STR4)
        f_new.write(PL_HL_OUT_STR5)
        f_new.write(PL_HL_OUT_STR6)
        f_new.write(PL_HL_OUT_STR7)
        f_new.write(PL_HL_OUT_STR8)
    f_new.write(END_STR)

def map_test():
    f_base = open('static/base_map.txt', 'r')
    base_str = ''
    for line in f_base:
        base_str = base_str + line
    f_new = open('templates/test_map.html', 'w')
    f_new.write(base_str)
    f_new.write(MK_STR1)
    f_new.write(MK_STR15)
    f_new.write(MK_STR2)
    # f_new.write(MK_PU_STR1)
    f_new.write(MK_PU_STR2)
    f_new.write(MK_PU_STR3)
    f_new.write(MK_PU_STR4)
    f_new.write(PL_STR1)
    f_new.write(PL_STR15)
    f_new.write(PL_STR2)
    f_new.write(END_STR)