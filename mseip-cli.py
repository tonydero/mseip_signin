# Created on 07-01-2018 15:26
# by Tony DeRocchis

# ask for password from mentor when the application is first started
import getpass
from hashlib import sha512
pass_file = './pass_file'
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
import os
from pathlib import Path
from distutils.util import strtobool
from time import sleep
import sys
import smtplib
from email.mime.text import MIMEText


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
cours_ref.append('Other')  # keep last
dua_file = './dua_file'  # using v4
key_file = './key_file'
db_dir = Path.home() / 'MSEIP_DB'
student_info_file = db_dir / 'student_info.csv'
time_log_file = db_dir / 'time_log.csv'

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def signIn(key_val):
    bann_id = input('Welcome to ECE Peer Mentoring!\n\n'
                    'Please swipe your Aggie ID or enter your ID#: ')
    len_id = len(bann_id)
    # check to see if card was swiped
    if len_id == 98:
        bann_id = bann_id[52:61]
    # check to make sureCourses ID is correct (as much as possible)
    unchkd_id = True
    while unchkd_id:
        if len_id == 6:
            bann_id = '800' + bann_id
            unchkd_id = False
        elif len_id < 9 or len_id > 9:
            bann_id = input('Invalid ID#\n'
                            'Please swipe your Aggie ID or enter your ID#: ')
        elif len_id == 9:
            if bann_id.startswith('800'):
                unchkd_id = False
            else:
                bann_id = input('Invalid ID#\n'
                                'Please swipe your Aggie ID or enter your'
                                ' ID#: ')
    #print(bann_id); sleep(3)  # FOR DEBUGGING

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
                                         'reason'] + cours_ref)
        Path.mkdir(db_dir, exist_ok=True)

    # check database for ID
    curr_time = d.datetime.now().strftime('%Y%m%d_%H%M%S')
    if bann_id_hash in set(student_info.index):
        returning = True
        # load values from database
        ovr_18 = student_info.loc[bann_id_hash, 'over18']
        dua_all = student_info.loc[bann_id_hash, 'DUA']
        dua_prof = student_info.loc[bann_id_hash, 'ProfUse']
        logd_in_index = time_log.loc[time_log['hashedID'] ==  \
                                     bann_id_hash].index.max()
        logd_in = time_log.iloc[logd_in_index, 1]
        if logd_in:
            # update id in previous entry to no_id_hash
            if not ovr_18:
                time_log.iloc[logd_in_index, 0] = no_id_hash
            time_log = time_log.append({'hashedID': no_id_hash,
                                        'loggedIn': False,
                                        'logTime': curr_time,
                                        'reason': 'log out'},
                                       ignore_index=True)
            time_log.to_csv(time_log_file)
            if (not ovr_18 or not dua_all) and dua_prof:
                print('Your personal data has been discarded.')
            elif not dua_prof:
                print('All of your data has been discarded.')
            print('Thank you for using ECE Peer Mentoring! Have a great day!')
            sleep(4)
            return

        if (not ovr_18 or not dua_all) and dua_prof:
            print('Your personal data will be discarded after this session.')
            sleep(3)
        elif not dua_prof:
            print('All of your data will be discarded after this session.')
            sleep(3)
        cls()
    # if student never has attended any mentoring or SI session
    else:
        returning = False
        cls()
        # present data use agreement
        with open(dua_file, 'r') as fin:
            print(fin.read())
        while True:
            try:
                ovr_18 = strtobool(input('Are you 18 years of age or older? '))
                break
            except ValueError:
                print('Incorrect response. Please answer yes or no.')

        email = input('Email: ')
        # need something to trigger sending the email *************************
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

    cours_resp = []
    for i, course_name in enumerate(cours_ref):
        while True:
            try:
                cours_resp.append(strtobool(input('Are you here for ' +
                                 course_name + ' (y/n)? ')))
                break
            except ValueError:
                print('Invalid response. Please answer yes or no.')

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

    return

# read key file for seeding sha hash
with open(key_file, 'r') as keyf:
    key_val = keyf.read()

while True:
    cls()
    signIn(key_val)

