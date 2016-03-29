#!/usr/bin/env python
from __future__ import division
import json
import sys

filepath = sys.argv[1]
f = open(filepath, 'r')
list = f.readlines()
dict = {}
f.close()

key_dict = {'Iner frankfurt.wanmei.com': 'iner_frankfurt',
            'Iner hk.wanmei.com': 'iner_hk',
            'Iner sng.wanmei.com': 'iner_sng',
            'Iner tok.wanmei.com': 'iner_tok',
            'Outer frankfurt': 'outer_frankfurt',
            'Outer hk': 'outer_hk',
            'Outer sng': 'outer_sng',
            'Outer tok': 'outer_tok',
            'Russian': 'Russian',
            'Taiwan': 'Taiwan',
            'Japan': 'Japan',
            'Korea': 'Korea',
            'Indonesia': 'Indonesia',
            'Malaysia': 'Malaysia',
            'Thailand': 'Thailand',
            'Beijing': 'Beijing'}

key_list = ['Iner frankfurt.wanmei.com',
            'Iner hk.wanmei.com',
            'Iner sng.wanmei.com',
            'Iner tok.wanmei.com',
            'Outer frankfurt',
            'Outer hk',
            'Outer sng',
            'Outer tok',
            'Russian',
            'Taiwan',
            'Japan',
            'Korea',
            'Indonesia',
            'Malaysia',
            'Thailand',
            'Beijing']

location = locals()
for key in key_list:
    location[u'num_list_{0:s}'.format(key_dict[key])] = []
for i, j in enumerate(list):
    for key in key_list:
        # location['num_list_%s'%key_dict['key']] = []
        if key in j:
            location[u'num_list_{0:s}'.format(key_dict[key])].append(i)
    dict[i] = j

for key in key_list:
    loss_count = 0
    speed_count_max = 0
    speed_count_avg = 0
    speed_count_min = 0
    for num in location[u'num_list_{0:s}'.format(key_dict[key])]:
        loss = dict[num + 1]
        loss_lv = loss.split(':')[1]
        loss_shu = loss_lv.split('%')[0]
        loss_final = loss_shu.strip()
        loss_int = int(loss_final)
        loss_count += loss_int
        # speed
	if loss_int != 100:
            speed = dict[num + 2]
            speed_dict = json.loads(speed)
            speed_max_int = int(round(float(speed_dict['max'])))
            speed_count_max += speed_max_int

            speed_avg_int = int(round(float(speed_dict['avg'])))
            speed_count_avg += speed_avg_int

            speed_min_int = int(round(float(speed_dict['min'])))
            speed_count_min += speed_min_int

    print '{1} loss package is {0} %'.format(
        int(round(float(loss_count / len(location[u'num_list_{0:s}'.format(key_dict[key])]))))
        , key_dict[key])
    print '{0} max is {1}'.format(key_dict[key],
                                  speed_count_max / len(location[u'num_list_{0:s}'.format(key_dict[key])]))
    print '{0} avg is {1}'.format(key_dict[key],
                                  speed_count_avg / len(location[u'num_list_{0:s}'.format(key_dict[key])]))
    print '{0} min is {1} \n'.format(key_dict[key],
                                     speed_count_min / len(location[u'num_list_{0:s}'.format(key_dict[key])]))

    # print len(location[u'num_list_{0:s}'.format(key_dict[key])])


# loss_count = 0
# speed_count_max = 0
# speed_count_avg = 0
# speed_count_min = 0
# for num in num_list:
#     loss = dict[num + 1]
#     loss_lv = loss.split(':')[1]
#     loss_shu = loss_lv.split('%')[0]
#     loss_final = loss_shu.strip()
#     loss_int = int(loss_final)
#     loss_count += loss_int
#     # speed
#     speed = dict[num + 2]
#     speed_dict = json.loads(speed)
#     speed_max_int = int(round(float(speed_dict['max'])))
#     speed_count_max = speed_count_max + speed_max_int
#
#     speed_avg_int = int(round(float(speed_dict['avg'])))
#     speed_count_avg += speed_avg_int
#
#     speed_min_int = int(round(float(speed_dict['min'])))
#     speed_count_min += speed_min_int

# print loss_count
# print 'max', speed_count_max / len(num_list)
# print 'avg', speed_count_avg / len(num_list)
# print 'min', speed_count_min / len(num_list)
