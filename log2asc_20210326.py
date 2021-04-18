import os
import time
from collections import deque
import shutil
from math import pi, cos, sin
import matplotlib.pyplot as plt
import numpy as np
import sys
from collections import deque
radius_of_earth = 6378137.0  # in meters
speedOfLight = 299792458.0  # in m/s
gpsPi = 3.1415926535898  # Definition of Pi used in the GPS coordinate system


def gps_distance(lat1, lon1, lat2, lon2):
    '''return distance between two points in meters,
    coordinates are in degrees
    thanks to http://www.movable-type.co.uk/scripts/latlong.html'''
    from math import radians, cos, sin, sqrt, atan2
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    dLat = lat2 - lat1
    dLon = lon2 - lon1

    a = sin(0.5 * dLat) ** 2 + sin(0.5 * dLon) ** 2 * cos(lat1) * cos(lat2)
    c = 2.0 * atan2(sqrt(a), sqrt(1.0 - a))
    return radius_of_earth * c


def gps_bearing(lat1, lon1, lat2, lon2):
    '''return bearing between two points in degrees, in range 0-360
    thanks to http://www.movable-type.co.uk/scripts/latlong.html'''
    from math import sin, cos, atan2, radians, degrees
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    dLat = lat2 - lat1
    dLon = lon2 - lon1
    y = sin(dLon) * cos(lat2)
    x = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dLon)
    bearing = degrees(atan2(y, x))
    if bearing < 0:
        bearing += 360.0
    return bearing


def encode_rkt_data(x, y, vx, vy):
    line = list()
    line.append(hex(int(np.median([x, 0, 655.35]) / 0.01) & 0xffff))
    line.append(hex(int(np.median([y, -327.68, 327.67]) / 0.01) & 0xffff))
    line.append(hex(int(np.median([vx, -327.68, 327.67]) / 0.01) & 0xffff))
    line.append(hex(int(np.median([vy, -327.68, 327.67]) / 0.01) & 0xffff))
    return line


def encode_rkt_data2(x, y, vx, vy, ax, ay):
    # line = list()
    # line.append(hex(int(np.median([x, 0, 655.35]) / 0.01) & 0xffff))
    # line.append(hex(int(np.median([y, -12.8, 12.8]) / 0.1) & 0xff))
    # line.append(hex(int(np.median([vx, -327.68, 327.67]) / 0.01) & 0xffff))
    # line.append(hex(int(np.median([vy, -12.8, 12.8]) / 0.1) & 0xff))
    # line.append(hex(int(np.median([ax, -12.8, 12.8]) / 0.1) & 0xff))
    # line.append(hex(int(np.median([ay, -12.8, 12.8]) / 0.1) & 0xff))
    # return line
    encode_x = hex(int(np.median([x, 0, 655.35]) / 0.01) & 0xffff)[2:].zfill(4)
    encode_y = hex(int(np.median([y, -12.8, 12.8]) / 0.1) & 0xff)[2:].zfill(2)
    encode_vx = hex(int(np.median([vx, -327.68, 327.67]) / 0.01) & 0xffff)[2:].zfill(4)
    encode_vy = hex(int(np.median([vy, -12.8, 12.8]) / 0.1) & 0xff)[2:].zfill(2)
    encode_ax = hex(int(np.median([ax, -12.8, 12.8]) / 0.1) & 0xff)[2:].zfill(2)
    encode_ay = hex(int(np.median([ay, -12.8, 12.8]) / 0.1) & 0xff)[2:].zfill(2)
    encode_str = '{} {} {} {} {} {} {} {}'.format(encode_x[0:2], encode_x[2:4],
                                        encode_y, encode_vx[0:2], encode_vx[2:4], encode_vy, encode_ax, encode_ay)
    return encode_str


def convert_rtk(filename):
    #pinpoint = {'lat': 22.537171, 'lon': 113.890032, 'height': 8.653500}
    pinpoint = {}
    hostpoint = {}
    if not pinpoint:
        with open(filename) as rf:
            for line in rf:
                cols = line.strip().split()
                if 'pinpoint' in cols[2]:
                    pinpoint['lat'] = float(cols[5])
                    pinpoint['lon'] = float(cols[6])
                    pinpoint['height'] = float(cols[7])
                    #print(pinpoint)
    if pinpoint:
        out_path = './log_rtk.txt'
        wf = open(out_path, 'w')
        with open(filename) as rf:
            for line in rf:
                cols = line.strip().split()
                ts = int(int(cols[0]) * 1e6 + int(cols[1]))
                if 'bestpos' in cols[2]:
                    hostpoint[ts] = dict()
                    hostpoint[ts]['lat'] = float(cols[5])
                    hostpoint[ts]['lon'] = float(cols[6])
                    hostpoint[ts]['ts'] = cols[0] + ' ' + cols[1]
                elif 'bestvel' in cols[2]:
                    if ts in hostpoint.keys():
                        hostpoint[ts]['hor_speed'] = float(cols[7])
                        hostpoint[ts]['trk_gnd'] = float(cols[8])
                elif 'heading' in cols[2]:
                    if ts in hostpoint.keys():
                        hostpoint[ts]['yaw'] = float(cols[6])
                else:
                    wf.write(line)

        key_sorted = sorted(hostpoint.keys())

        n = 20
        tmp_vx = deque(maxlen=n)
        tmp_vy = deque(maxlen=n)
        acc_x = 0
        # calculate the distance and the angle
        for i in range(0, len(key_sorted)):
            dist = gps_distance(pinpoint['lat'], pinpoint['lon'],\
                                hostpoint[key_sorted[i]]['lat'], hostpoint[key_sorted[i]]['lon'])
            angle = gps_bearing(pinpoint['lat'], pinpoint['lon'],\
                                hostpoint[key_sorted[i]]['lat'], hostpoint[key_sorted[i]]['lon'])
            if 'yaw' not in hostpoint[key_sorted[i]] or 'trk_gnd' not in hostpoint[key_sorted[i]]:
                continue
            angle = angle - hostpoint[key_sorted[i]]['yaw']

            trk_host = hostpoint[key_sorted[i]]['trk_gnd'] + 180.0
            if trk_host > 360:
                trk_host = trk_host - 360.0

            theta = hostpoint[key_sorted[i]]['trk_gnd'] - hostpoint[key_sorted[i]]['yaw']
            vel_x = hostpoint[key_sorted[i]]['hor_speed'] * cos(theta * pi / 180)
            vel_y = hostpoint[key_sorted[i]]['hor_speed'] * sin(theta * pi / 180)

            tmp_vx.append(vel_x)
            tmp_vy.append(vel_y)
            if len(tmp_vx) < n:
                continue
            # acc_x = (tmp_vx[-1] - tmp_vx[0])/(0.05 * n)
            acc_x = 0.9 * acc_x + 0.1 * (tmp_vx[-1] - tmp_vx[-2])/(0.05)
            acc_y = (tmp_vy[-1] - tmp_vy[0])/(0.05 * n)

            pos_x = cos(angle * pi / 180.0) * dist
            pos_y = sin(angle * pi / 180.0) * dist
            # encode_data = encode_rkt_data(pos_x, pos_y, vel_x, vel_y)
            encode_str = encode_rkt_data2(pos_x, pos_y, vel_x, vel_y, acc_x, acc_y)

            print('{} CAN0 0x100 {}'.format(hostpoint[key_sorted[i]]['ts'], encode_str), file=wf)
        shutil.copy2(os.path.abspath(out_path), os.path.dirname(filename))
        return os.path.abspath(out_path)


def time_sort(file_name, sort_itv=8000):
    """
    sort the log lines according to timestamp.
    :param file_name: path of the log file
    :param sort_itv:
    :return: sorted file path

    """
    # rev_lines = []
    past_lines = deque(maxlen=2 * sort_itv)
    wf = open('log_sort.txt', 'w')
    idx = 0
    with open(file_name) as rf:
        for idx, line in enumerate(rf):
            cols = line.split(' ')
            tv_s = int(cols[0])
            tv_us = int(cols[1])
            ts = tv_s * 1000000 + tv_us
            past_lines.append([ts, line])
            # print(len(past_lines))
            if len(past_lines) < 2 * sort_itv:
                continue
            if (idx + 1) % sort_itv == 0:
                # print(len(past_lines))
                past_lines = sorted(past_lines, key=lambda x: x[0])
                wf.writelines([x[1] for x in past_lines[:sort_itv]])
                past_lines = deque(past_lines, maxlen=2 * sort_itv)
            # if len(past_lines) > 300:  # max lines to search forward.
            #     wf.write(past_lines.popleft()[1])
    past_lines = sorted(past_lines, key=lambda x: x[0])
    wf.writelines([x[1] for x in past_lines[sort_itv - ((idx + 1) % sort_itv):]])

    wf.close()
    return os.path.abspath('log_sort.txt')

def log2asc(logfilename, ascfilename):
    log_vector = open(ascfilename, 'w')
    filestatbuf = os.stat(logfilename)
    log_vector.write('date ')
    log_vector.write(time.ctime(filestatbuf.st_mtime))
    log_vector.write('\n')
    log_vector.write('base hex  timestamps absolute\n')
    log_vector.write('internal events logged\n')
    log_vector.write('//loging with PCC system , translation to vector form \n')
    log_vector.write('//CAN channel +1  即 PCC 系统 CAN 0，1，2，3  vector 转为 CAN 1,2,4\n')

    time_init = 0

    with open(logfilename) as logfile:
        for line in logfile:
            temp_line = line.split()
            if temp_line[2][:3] == 'CAN':
                if time_init == 0:
                    time_init = float(temp_line[0] + '.' + temp_line[1])
                new_time = float(temp_line[0] + '.' + temp_line[1]) - time_init
                log_vector.write(str(new_time))
                log_vector.write(' ')
                log_vector.write(str(int(temp_line[2][3]) + 1))
                log_vector.write(' ')
                if len(temp_line[3]) > 6:
                    log_vector.write(temp_line[3][2:])
                    log_vector.write('x')
                else:
                    log_vector.write(temp_line[3][2:])

                log_vector.write(' ')
                log_vector.write('Rx')
                log_vector.write(' ')
                log_vector.write('d')
                log_vector.write(' ')
                log_vector.write('8')
                log_vector.write(' ')
                #log_vector.write(' '.join(temp_line[4:]))
                if len(temp_line[4]) > 2:
                    for num in range(0, len(temp_line[4]) + 1):
                        if num % 2 == 0:
                            log_vector.write(' ')
                            log_vector.write(temp_line[4][num:num + 2])
                else:
                    log_vector.write(' ')
                    log_vector.write(' '.join(temp_line[4:]))
                log_vector.write('\n')

    log_vector.close()



if __name__ == "__main__":
    # search_path = "F:\\H7_1242\\cvedata\\0317\\动态行人_CPFA"
    search_path = "F:\\H7_1242\\log"
    target_txt1 = "log.txt"
    target_txt2 = "log_rtk.txt"
    terminal_txt1 = "log_vector.asc"
    terminal_txt2 = "log_rtk_vector.asc"

    for root, dirs, files in os.walk(search_path):
        if target_txt1 in files:
            if target_txt2 in files:
                os.remove(os.path.join(root, target_txt2))
                print("removing file: " + os.path.join(root, target_txt2))
            logfilename = os.path.join(root, "log.txt")
            sort_src = time_sort(logfilename)
            shutil.copy2(sort_src, os.path.dirname(logfilename))
            print('processing log: {}'.format(logfilename))
            os.remove(sort_src)
            convert_rtk(logfilename)

    for root, dirs, files in os.walk(search_path):
        if target_txt2 in files:
            if terminal_txt2 in files:
                os.remove(os.path.join(root, terminal_txt2))
                print("removing file: " + os.path.join(root, terminal_txt2))
            candidate = os.path.join(root, "log_rtk_vector.asc")
            logfilename = os.path.join(root, "log_rtk.txt")
            log2asc(logfilename, candidate)
            print("creating file: " + candidate)

        elif target_txt1 in files:
            if terminal_txt1 in files:
                os.remove(os.path.join(root, terminal_txt1))
                print("removing file: " + os.path.join(root, terminal_txt1))
            candidate = os.path.join(root, "log_vector.asc")
            logfilename = os.path.join(root, "log.txt")
            log2asc(logfilename, candidate)
            print("creating file: " + candidate)

