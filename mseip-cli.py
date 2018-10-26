# Created on 07-01-2018 15:26
# by Tony DeRocchis

# ask for password from mentor when the application is first started
import getpass
from hashlib import sha512
from pathlib import Path
db_dir = Path.home() / 'MSEIP_DB'
pass_file = './pass_file'


print('DB storage location: ', str(db_dir))
with open(pass_file, 'r') as passf:
    pass_chk = passf.read()
pass_wrong = True
while pass_wrong:
    h = sha512()
    h.update(bytes(getpass.getpass('Password (will not show):'),
             encoding='ascii'))
    password = h.hexdigest()
    #password = pass_chk  # ONLY FOR DEBUGGING ********************************
    if password == pass_chk:
        pass_wrong = False
    else:
        print('Incorrect password.')

# once password is correctly enter, import and define everything else
import datetime as d
import pandas as pd
import numpy as np
import os
from distutils.util import strtobool
from time import sleep, time
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
from cryptography.fernet import Fernet


cours_ref = []
cours_ref.append('EE100 Intro to ECE')
cours_ref.append('EE112 Embedded Systems')
cours_ref.append('EE200 Linear Alg., Prob., and Stats App.')
cours_ref.append('EE212 Intro to Computer Organization')
cours_ref.append('EE230 AC Circuits and Intro to Power')
cours_ref.append('EE240 Multivar. Vector Calculus App.')
cours_ref.append('EE317 Semiconductors & Electronics')
cours_ref.append('EE320 Signals & Systems I')
cours_ref.append('EE325 Signals & Systems II')
cours_ref.append('EE340 Fields & Waves')
cours_ref.append('Other Course')  # keep last
dua_file = './dua_file'  # using v4
key_file = './key_file'
smtp_file = './smtp_file'
fernet_key = './fernet_key'
student_info_file = db_dir / 'student_info.csv'
time_log_file = db_dir / 'time_log.csv'

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def signIn(key_val, bann_id, logd_in_ids, server):
    # hash ID
    h = sha512()
    h.update(bytes(key_val+bann_id, encoding='ascii'))
    bann_id_hash = h.hexdigest()
    h = sha512()
    h.update(b'noID')
    no_id_hash = h.hexdigest()

    # read core enrollment and time log database files if the DB exists
    if (Path.is_file(student_info_file) and
            Path.is_file(time_log_file)):
        student_info = pd.read_csv(student_info_file, index_col=0)
        time_log = pd.read_csv(time_log_file, index_col=0)
    else:
        student_info = pd.DataFrame(columns=['over18','DUA','ProfUse','email'])
        # loggedIn binary (true if student has not logged out)
        time_log = pd.DataFrame(columns=['hashedID','loggedIn','logTime',
                                         'logDuration','reason'] + cours_ref)
        Path.mkdir(db_dir, exist_ok=True)

    # check database for ID
    curr_time = time()
    if bann_id_hash in set(student_info.index):
        returning = True
        # load values from database
        ovr_18 = student_info.loc[bann_id_hash, 'over18']
        dua_all = student_info.loc[bann_id_hash, 'DUA']
        dua_prof = student_info.loc[bann_id_hash, 'ProfUse']
        # check for ID in last 100 time log entries, because under 18s
        #if bann_id_hash in set(time_log['hashedID'][-100:]):
        if bann_id_hash not in logd_in_ids:
            logd_in_index = time_log.loc[time_log['hashedID'] ==  \
                                         bann_id_hash].index.max()
            logd_in = time_log.iloc[logd_in_index, 1]
            logd_in_time = time_log.iloc[logd_in_index, 2]
            logd_in_dur = curr_time - logd_in_time
            logd_in_ids.append(bann_id_hash)
        else:
            logd_in = False
            logd_in_ids.remove(bann_id_hash)

        if logd_in:
            # update id in previous entry to no_id_hash
            if not ovr_18 and not dua_prof:
                time_log.iloc[logd_in_index, 0] = no_id_hash
                time_log = time_log.append({'hashedID': no_id_hash,
                                            'loggedIn': False,
                                            'logTime': curr_time,
                                            'logDuration': logd_in_dur,
                                            'reason': 'log out'},
                                           ignore_index=True)
            else:
                time_log = time_log.append({'hashedID': bann_id_hash,
                                            'loggedIn': False,
                                            'logTime': curr_time,
                                            'logDuration': logd_in_dur,
                                            'reason': 'log out'},
                                           ignore_index=True)

            time_log.to_csv(time_log_file)
            if (not ovr_18 or not dua_all) and dua_prof:
                print('Your personal data have been discarded.')
            elif not dua_prof:
                print('All of your data have been discarded.')
            print('Thank you for using ECE Peer Mentoring! Have a great day!')
            sleep(4)
            return logd_in_ids

        #if (not ovr_18 or not dua_all) and dua_prof:
        #    print('Your personal data will be discarded after this session.')
        #    sleep(3)
        #elif not dua_prof:
        #    print('All of your data will be discarded after this session.')
        #    sleep(3)
    # if student never has attended any mentoring or SI session
    else:
        returning = False
        cls()
        # present data use agreement
        with open(dua_file, 'r',encoding='utf-8') as fin:
            dua = fin.read()
            print(dua)
        while True:
            try:
                ovr_18 = strtobool(input('Are you 18 years of age or older? '))
                break
            except ValueError:
                print('Incorrect response. Please answer yes or no.')

        email = input('Email: ')
        while not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            print('Invalid email.')
            email = input('Email: ')
        # send email copy of DUA
        fromaddr = 'NMSU_MSEIP@nmsu.edu'
        dua_email = MIMEMultipart()
        dua_email['From'] = fromaddr
        dua_email['To'] = email
        dua_email['Subject'] = "NMSU Peer Mentoring Data Use Agreement"
        preamble = ('Hello,\n\nBelow you will find the Data Use '
                    'Agreement for the NMSU ECE Peer Mentoring '
                    'sign-in application.\n\n')
        dua_msg = MIMEText(preamble+dua, 'plain')
        dua_email.attach(dua_msg)
        server.sendmail(fromaddr,email,dua_email.as_string())

        if ovr_18:
            while True:
                try:
                    dua_ques = ('Do you consent for data collection as '
                                'described above? ')
                    dua_all = strtobool(input(dua_ques))
                    break
                except ValueError:
                    print('Incorrect response. Please answer yes or no.')
            if not dua_all:
                while True:
                    try:
                        prof_ques = ('Do you consent for data collection only '
                                     'for the purpose of providing your '
                                     'course instructor(s) with attendence '
                                     'information?')
                        dua_prof = strtobool(input(prof_ques))
                        break
                    except ValueError:
                        print('Incorrect response. Please answer yes or no.')
        else:
            dua_all = False
            while True:
                try:
                    prof_ques = ('Is(Are) your course instructor(s) providing '
                                 'credit for your attendance? (Data will be '
                                 'collected only for the purpose of providing '
                                 'attendance information to your course '
                                 'instructor(s) ')
                    dua_prof = strtobool(input(prof_ques))
                    break
                except ValueError:
                    print('Incorrect response. Please answer yes or no.')
        if dua_all:
            dua_prof = True

        cls()
        # create new row to be appended to student_info database
        student_info.index
        student_info.head()
        new_student_info = pd.DataFrame({'over18': ovr_18,
                                         'DUA': dua_all,
                                         'ProfUse': dua_prof,
                                         'email': email},
                                        index=[bann_id_hash])
        student_info = student_info.append(new_student_info)
        student_info.head()

    cours_resp = np.zeros(len(cours_ref)).tolist()
    for i, course_name in enumerate(cours_ref):
        print(str(i+1) + ') ' + course_name)
        #while True:
        #    try:
        #        cours_resp.append(strtobool(input('Are you here for ' +
        #                         course_name + ' (y/n)? ')))
        #        break
        #    except ValueError:
        #        print('Invalid response. Please answer yes or no.')
    cours_resp_str = input('Please enter a comma-seperated list of the'
                            ' numbers next to the courses you are here to get'
                            ' help with: ')

    # convert cours_resp_str to indices
    crs = cours_resp_str.split()
    crs = [crs[x].split(',') for x,val in enumerate(crs)]
    if len(crs) > 1:
        if type(crs[0]) == list:
            crs = [int(x) for x in np.array([y[0] for y in crs])]
        else:
            crs = [int(x) for x in np.array(crs)]
    else:
        crs = [int(x) for x in np.array(crs[0])]

    print(crs)

    #use converted indices to indicate course responses
    for z in crs:
        cours_resp[z-1] = 1
    cours_resp = [int(x) for x in cours_resp]
    print(cours_resp)

    # if last course (other) is true, set it to their response
    if cours_resp[-1]:
        cours_resp[-1] = input('What other course(s) are you here for? ')

    att_reas = input('What are you here for today? (Homework, exam, etc.) ')

    cls()

    if ovr_18 and dua_all:
        # append time_log values
        time_log = time_log.append({'hashedID': bann_id_hash,
                                    'loggedIn': True,
                                    'logTime': curr_time,
                                    'reason': att_reas},
                                   ignore_index=True)
        time_log.loc[time_log.index.max(), cours_ref] = cours_resp

    elif dua_prof:
        # append time_log values except the reason
        time_log = time_log.append({'hashedID': bann_id_hash,
                                    'loggedIn': True,
                                    'logTime': curr_time,
                                    'reason': 'NA'},
                                   ignore_index=True)
        time_log.loc[time_log.index.max(), cours_ref] = cours_resp

    else:
        # append time_log values except the ID, reason, or courses
        time_log = time_log.append({'hashedID': bann_id_hash,
                                    'loggedIn': True,
                                    'logTime': curr_time,
                                    'reason': 'NA'},
                                   ignore_index=True)
        time_log.loc[time_log.index.max(), cours_ref] = 'NA'

    time_log.to_csv(time_log_file)
    student_info.to_csv(student_info_file)
    if (not ovr_18 or not dua_all) and dua_prof:
        print('Your personal data will be discarded after this session.')
        sleep(3)
    elif not dua_prof:
        print('All of your data will be discarded after this session.')
        sleep(3)

    return logd_in_ids

# read in password from file for the smtp server
with open(fernet_key, 'r') as f:
    key_str = f.read()
with open(smtp_file, 'r') as f:
    smtp_str = f.read()
c = Fernet(bytes(key_str,encoding='utf-8'))
smtp_pass = c.decrypt(bytes(smtp_str,encoding='utf-8')).decode('utf-8')
server = smtplib.SMTP('smtp.nmsu.edu',587)
server.login('NMSU_MSEIP@nmsu.com', smtp_pass)
#server = smtplib.SMTP('localhost',1025)

# read key file for seeding sha hash
with open(key_file, 'r') as keyf:
    key_val = keyf.read()

logd_in_ids = []

while True:
    cls()
    print('                  Welcome to')
    print('          _   _ __  __  _____ _    _ ')
    print('         | \ | |  \/  |/ ____| |  | |')
    print('         |  \| | \  / | (___ | |  | |')
    print('         | . ` | |\/| |\___ \| |  | |')
    print('         | |\  | |  | |____) | |__| |')
    print('         |_| \_|_|  |_|_____/ \____/ ')
    print('\n             ECE Peer Mentoring!\n')
    bann_id = input('Please swipe your Aggie ID or enter your ID#:\n')
    # check to make sure ID is correct (as much as possible)
    unchkd_id = True
    while unchkd_id:
        # for logging everyone out and shutting down the application
        if bann_id.lower() in ['0','q','quit','e','exit']:
            quit_sure = strtobool(input('Are you sure you want to shut down '
                                        'the app and log everyone out? '))
            if quit_sure:
                curr_time = time()
                for bann_id_hash in logd_in_ids:
                    # load values from database
                    student_info = pd.read_csv(student_info_file, index_col=0)
                    time_log = pd.read_csv(time_log_file, index_col=0)
                    ovr_18 = student_info.loc[bann_id_hash, 'over18']
                    dua_all = student_info.loc[bann_id_hash, 'DUA']
                    dua_prof = student_info.loc[bann_id_hash, 'ProfUse']
                    logd_in_index = time_log.loc[time_log['hashedID'] ==  \
                                                 bann_id_hash].index.max()
                    logd_in_time = time_log.iloc[logd_in_index, 2]
                    logd_in_dur = curr_time - logd_in_time

                    # update id in previous entry to no_id_hash
                    if not ovr_18 and not dua_prof:
                        time_log.iloc[logd_in_index, 0] = no_id_hash
                        time_log = time_log.append({'hashedID': no_id_hash,
                                                    'loggedIn': False,
                                                    'logTime': curr_time,
                                                    'logDuration': logd_in_dur,
                                                    'reason': 'log out'},
                                                   ignore_index=True)
                    else:
                        time_log = time_log.append({'hashedID': bann_id_hash,
                                                    'loggedIn': False,
                                                    'logTime': curr_time,
                                                    'logDuration': logd_in_dur,
                                                    'reason': 'log out'},
                                                   ignore_index=True)

                    time_log.to_csv(time_log_file)
                server.quit()
                raise SystemExit('All students are now logged out.\nThanks for'
                                 ' using the NMSU ECE Peer Mentoring sign-in'
                                 ' application!')
        len_id = len(bann_id)
        # check to see if card was swiped
        if len_id == 98:
            bann_id = bann_id[52:61]
        # checks to make sure care read correctly or manual input correct
        if len_id == 6:
            bann_id = '800' + bann_id
            unchkd_id = False
        elif len_id < 9 or len_id > 9:
            bann_id = input('Invalid ID#\n'
                            'Please swipe your Aggie ID or enter your ID#:\n')
        elif len_id == 9:
            if bann_id.startswith('800'):
                unchkd_id = False
            else:
                bann_id = input('Invalid ID#\n'
                                'Please swipe your Aggie ID or enter your'
                                ' ID#:\n')
        else:
            bann_id = input('Invalid ID#\n'
                            'Please swipe your Aggie ID or enter your ID#:\n')
    #print(bann_id); sleep(3)  # FOR DEBUGGING
    logd_in_ids = signIn(key_val, bann_id, logd_in_ids, server)

