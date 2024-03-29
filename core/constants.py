# -*- coding: utf-8 -*-

WEEK_DAYS = [u'mon', u'tue', u'wed', u'thu', u'fri', u'sat', u'sun']
WEEK_DAYS_KOR = [u'월', u'화', u'수', u'목', u'금', u'토', u'일']
WEEK_DAY_KEYS = [u'yoil2', u'yoil3', u'yoil4', u'yoil5', u'yoil6', u'yoil7', u'yoil0']  # 월화수목금토 미지정
WEEK_DAY_TRANS = {WEEK_DAY_KEYS[i]:WEEK_DAYS[i] for i in range(len(WEEK_DAY_KEYS))}
WEEK_DAY_TRANS_KOR = {WEEK_DAY_KEYS[i]:WEEK_DAYS_KOR[i] for i in range(len(WEEK_DAY_KEYS))}
WEEK_DAY_TRANS_KOR_REVERSE = {WEEK_DAYS_KOR[i]:WEEK_DAY_KEYS[i] for i in range(len(WEEK_DAYS_KOR))}

TIME_TABLE_PERIODS = [
    ('0800', '0830'),
    ('0830', '0900'),
    ('0900', '0930'),
    ('0930', '1000'),
    ('1000', '1030'),
    ('1030', '1100'),
    ('1100', '1130'),
    ('1130', '1200'),
    ('1200', '1230'),
    ('1230', '1300'),
    ('1300', '1330'),
    ('1330', '1400'),
    ('1400', '1430'),
    ('1430', '1500'),
    ('1500', '1530'),
    ('1530', '1600'),
    ('1600', '1630'),
    ('1630', '1700'),
    ('1700', '1730'),
    ('1730', '1800'),
    ('1800', '1830'),
    ('1830', '1900'),
    ('1900', '1930'),
    ('1930', '2000'),
    ('2000', '2030'),
    ('2030', '2100'),
    ('2100', '2130'),
    ('2130', '2200'),
    ('2200', '2230'),
    ('2230', '2300'),
    ('2300', '2330'),
    ('2330', '2400')
]

TIME_TABLE_PERIODS_VERBOSE = [
    u'1교시 (08:00~08:30)',
    u'2교시 (08:30~09:00)',
    u'3교시 (09:00~09:30)',
    u'4교시 (09:30~10:00)',
    u'5교시 (10:00~10:30)',
    u'6교시 (10:30~11:00)',
    u'7교시 (11:00~11:30)',
    u'8교시 (11:30~12:00)',
    u'9교시 (12:00~12:30)',
    u'10교시 (12:30~13:00)',
    u'11교시 (13:00~13:30)',
    u'12교시 (13:30~14:00)',
    u'13교시 (14:00~14:30)',
    u'14교시 (14:30~15:00)',
    u'15교시 (15:00~15:30)',
    u'16교시 (15:30~16:00)',
    u'17교시 (16:00~16:30)',
    u'18교시 (16:30~17:00)',
    u'19교시 (17:00~17:30)',
    u'20교시 (17:30~18:00)',
    u'21교시 (18:00~18:30)',
    u'22교시 (18:30~19:00)',
    u'23교시 (19:00~19:30)',
    u'24교시 (19:30~20:00)',
    u'25교시 (20:00~20:30)',
    u'26교시 (20:30~21:00)',
    u'27교시 (21:00~21:30)',
    u'28교시 (21:30~22:00)',
    u'29교시 (22:00~22:30)',
    u'30교시 (22:30~23:00)',
    u'31교시 (23:00~23:30)',
    u'32교시 (23:30~24:00)'
]

GRADES_VERBOSE = [
    u'freshman',
    u'sophomore',
    u'junior',
    u'senior'
]

GRADES_VERBOSE_KOR = [
    u'1학년',
    u'2학년',
    u'3학년',
    u'4학년'
]

FIRST_SEMESTER = 10
SECOND_SEMESTER = 20
SUMMER_SEMESTER = 15
WINTER_SEMESTER = 25

SEMESTERS = [
    FIRST_SEMESTER,  # 1학기
    SECOND_SEMESTER,  # 2학기
    # 30,  # 여름
    # 40,  # 겨울
]

SEMESTERS_VERBOSE = [
    u'1학기',
    u'2학기'
]

SEMESTER_TRANS = [
    None,
    None,None,None,None,None,None,None,None,None,SEMESTERS_VERBOSE[0],
    None,None,None,None,None,None,None,None,None,SEMESTERS_VERBOSE[1],
]