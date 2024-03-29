# -*- coding: utf-8 -*-
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils.decorators import method_decorator
from core.constants import WEEK_DAY_KEYS, TIME_TABLE_PERIODS, WEEK_DAY_TRANS_KOR_REVERSE
from core.utils import fetch_student_time_table, get_current_year, get_current_semester, fetch_courses
import re


class UserManager(BaseUserManager):
    def create_user(self, userid, password, **extra_fields):
        user = self.model(userid=userid, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, userid, password, **extra_fields):
        user = self.create_user(userid, password, **extra_fields)
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True

        user.save(using=self._db)

        return user

    def create_student(self, userid, password, **extra_fields):
        user = self.create_user(userid, password, **extra_fields)
        student_group = Group.objects.get(name="students")

        user.groups.add(student_group)

        return user

    def create_inactive_student(self, userid, password, **extra_fields):
        user = self.create_student(userid, password, **extra_fields)

        user.is_active = False
        user.save(using=self._db)

        return user

    def get_or_create_student(self, userid, password, **extra_fields):
        student = self.students(userid=userid, is_active=True)
        if student:
            return student.get()

        student = self.students(userid=userid, is_active=False)
        if student:
            student = student.get()
            student.set_password(password)
            student.is_active = True
            student.save()

            return student

        return self.create_student(userid, password, **extra_fields)

    def create_professor(self, userid, password, **extra_fields):
        user = self.create_user(userid, password, **extra_fields)
        professor_group = Group.objects.get(name="professors")

        user.groups.add(professor_group)

        return user

    def create_inactive_professor(self, userid, password, **extra_fields):
        user = self.create_professor(userid, password, **extra_fields)

        user.is_active = False
        user.save(using=self._db)

        return user

    def students(self, *args, **kwargs):
        qs = self.get_queryset().filter(*args, **kwargs)
        return qs.filter(groups=Group.objects.get(name="students"))

    def professors(self, *args, **kwargs):
        qs = self.get_queryset().filter(*args, **kwargs)
        return qs.filter(groups=Group.objects.get(name="professors"))


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = u"사용자"
        verbose_name_plural = u"사용자들"
        swappable = "AUTH_USER_MODEL"

    USERNAME_FIELD = "userid"

    userid = models.CharField(verbose_name=u"아이디",
                              max_length=60,
                              help_text=u"아이디 혹은 학번",
                              unique=True,
                              db_index=True)

    name = models.CharField(verbose_name=u"이름",
                            max_length=64,
                            null=True,
                            blank=True)

    email = models.EmailField(verbose_name=u"Email",
                              max_length=255,
                              unique=True,
                              null=True)

    is_staff = models.BooleanField(verbose_name="is staff",
                                   default=False,
                                   help_text="Is this user a staff?")
    is_active = models.BooleanField(verbose_name="is active",
                                    default=True,
                                    help_text="Is this user active?")

    objects = UserManager()

    # only the user who is in the students group can call this method
    @method_decorator(transaction.atomic)
    def add_course(self):
        student_group = Group.objects.get(name="students")
        if student_group not in self.groups.all():
            return

        year = get_current_year()
        semester = get_current_semester()
        time_table_data = fetch_student_time_table(self.userid, year, semester)

        for period_index, period_data in enumerate(time_table_data):
            for day in WEEK_DAY_KEYS:
                if period_data[day]:
                    course_no, name, trash1, trash2, trash3 = period_data[day].split(',')
                    course = Course.objects.filter(year=year, semester=semester, course_no=course_no).get()
                    self.courses.add(course)

    def is_student(self):
        if self.groups.filter(name="students"):
            return True
        return False

    def is_professor(self):
        if self.groups.filter(name="professors"):
            return True
        return False

    def __unicode__(self):
        return u'{}({})'.format(self.userid, self.name)


def add_student(student_id):
    try:
        student = User.objects.get(userid=student_id)
    except User.DoesNotExist:
        student = User.objects.create_inactive_student(student_id, "00")

    try:
        student.add_course()
        return True, u'success', u'학번 {} 추가되었습니다'.format(student.userid)
    except Exception as e:
        return False, u'danger', u'학생 추가에 실패하였습니다'


class Univ(models.Model):
    organization_code = models.CharField(verbose_name=u'조직코드', max_length=30)
    univ_code = models.CharField(verbose_name=u'대학코드', max_length=30, primary_key=True)

    name = models.CharField(verbose_name=u'대학이름', max_length=60, null=True)

    def __unicode__(self):
        return u'{}({})'.format(self.name, self.univ_code)


class Department(models.Model):
    univ = models.ForeignKey(Univ, related_name='departments', null=True)

    department_code = models.CharField(verbose_name=u'학과코드', max_length=30, primary_key=True)

    name_ko = models.CharField(verbose_name=u'학과이름', max_length=150, null=True)
    name_en = models.CharField(verbose_name=u'학과이름(영문)', max_length=150, null=True)

    def __unicode__(self):
        return u'{}({})'.format(self.name_ko, self.department_code)


class CourseManager(models.Manager):
    @method_decorator(transaction.atomic)
    def create(self, year, semester, grade, name, name_en, course_no, time_infos):
        time_re = re.compile(
            r'[\d]{2}(:)?[\d]{2}'
        )

        try:
            course = Course.objects.filter(year=year, semester=semester, course_no=course_no).get()

        except Course.DoesNotExist:
            course = Course(year=year, semester=semester, grade=grade, course_no=course_no, name=name, name_en=name_en)
            course.save()

        course_times = course.course_times.all()

        for time_info in time_infos:
            start_time = time_info['start_time']
            end_time = time_info['end_time']

            if not (time_re.match(start_time) and time_re.match(end_time)):
                raise ValidationError(u'시간의 형식에 맞지 않습니다')

            if ":" in start_time:
                start_time = start_time[:2] + start_time[3:]
            if ":" in end_time:
                end_time = end_time[:2] + end_time[3:]

            for course_time in CourseTime.objects.filter(day=WEEK_DAY_TRANS_KOR_REVERSE[time_info['day']],
                                                         start_time__gte=start_time,
                                                         end_time__lte=end_time):
                if course_time not in course_times:
                    course.course_times.add(course_time)
        return course


class CourseTime(models.Model):
    WEEK_DAY_CHOICES = (
        (WEEK_DAY_KEYS[0], u'월요일'),
        (WEEK_DAY_KEYS[1], u'화요일'),
        (WEEK_DAY_KEYS[2], u'수요일'),
        (WEEK_DAY_KEYS[3], u'목요일'),
        (WEEK_DAY_KEYS[4], u'금요일'),
        (WEEK_DAY_KEYS[5], u'토요일'),
        (WEEK_DAY_KEYS[6], u'월요일')
    )

    day = models.CharField(verbose_name=u'요일', choices=WEEK_DAY_CHOICES, max_length=8, null=False, blank=False)
    period_index = models.IntegerField(verbose_name=u'교시', null=False, blank=False)
    start_time = models.CharField(verbose_name=u'시작시간', max_length=8, null=False, blank=False)
    end_time = models.CharField(verbose_name=u'종료시간', max_length=8, null=False, blank=False)

    def __unicode__(self):
        return u'{} {}~{}'.format(self.day, self.start_time, self.end_time)


class Course(models.Model):
    department = models.ForeignKey(Department, related_name='courses', null=True)
    students = models.ManyToManyField(User, related_name='courses')
    professor = models.ForeignKey(User, related_name='teaching_courses', null=True)
    course_times = models.ManyToManyField(CourseTime, related_name='courses')

    year = models.IntegerField(verbose_name=u'년도', null=False, blank=False)
    semester = models.IntegerField(verbose_name=u'학기', null=False, blank=False)
    grade = models.IntegerField(verbose_name=u'학년', null=False, blank=False)
    course_no = models.SlugField(verbose_name=u'학수번호', null=False, blank=False, unique=True)
    name = models.CharField(verbose_name=u'과목이름', max_length=128, null=False, blank=False)
    name_en = models.CharField(verbose_name=u'과목이름(영어)', max_length=128, null=False, blank=False)

    objects = CourseManager()

    def __unicode__(self):
        return u'{}-{}'.format(self.course_no, self.name)

    @staticmethod
    def update_courses(year, semester):
        print 'Getting course information from portal'
        course_info_list = fetch_courses(year, semester)
        total = len(course_info_list)

        print 'Inserting into the database'
        for index, course_info in enumerate(course_info_list, start=1):
            # year, semester, grade, name, course_no, time_infos
            time_info_list = list()
            if course_info['suupTimes']:
                for time in course_info['suupTimes'].split(','):
                    # 요일(start_time~end_time)
                    if len(time.split('(')) > 1:
                        day, rest = time.split('(')
                        start_time, end_time = rest[:-1].split('-')

                        time_info_list.append(dict(
                            day=day,
                            start_time=start_time,
                            end_time=end_time
                        ))

            professor_name = course_info['daepyoGangsaNm']
            professor_id = course_info['daepyoGangsaNo']
            try:
                professor = User.objects.filter(userid=professor_id).get()
            except:
                professor = User.objects.create_inactive_professor(professor_id, "0000", name=professor_name)

            course = Course.objects.create(year=year, semester=semester, grade=course_info['isuGrade'],
                                           name=course_info['gwamokNm'], name_en=course_info['gwamokEnm'],
                                           course_no=course_info['suupNo'], time_infos=time_info_list)
            professor.teaching_courses.add(course)

            print '[{}/{}]'.format(index, total)
        print 'Done'


class ExtraManager(models.Manager):
    @method_decorator(transaction.atomic)
    def create(self, year, semester, course_no, week, category, memo, day, start_time, end_time, **kwargs):
        course = Course.objects.filter(year=year, semester=semester, course_no=course_no).get()

        extra = Extra(course=course, week=week, category=category, memo=memo)
        extra.save()

        course_times = CourseTime.objects.filter(day=day, start_time__gte=start_time, end_time__lte=end_time)
        for course_time in course_times:
            extra.course_times.add(course_time)

        return extra


class Extra(models.Model):
    ADDITIONAL = 0
    EXAM = 1
    ASSIGNMENT = 2
    CANCEL = 3

    EXTRA_CATEGORY_CHOICES = (
        (ADDITIONAL, u'보강'),
        (EXAM, u'시험'),
        (ASSIGNMENT, u'과제'),
        (CANCEL, u'휴강')
    )

    course = models.ForeignKey(Course, related_name='extras')
    course_times = models.ManyToManyField(CourseTime, related_name='extras')

    week = models.IntegerField(verbose_name=u'주차', null=False, blank=False)
    category = models.IntegerField(verbose_name=u'유형', null=False, blank=False, choices=EXTRA_CATEGORY_CHOICES)
    memo = models.CharField(verbose_name=u'메모', max_length=256, null=True, blank=True)

    objects = ExtraManager()

    def __unicode__(self):
        return u'{} {} {}'.format(self.week, self.type, self.course.name)


