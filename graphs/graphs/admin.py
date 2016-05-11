# -*- coding: utf-8 -*-
from django.contrib import admin
from graphs.models import *

admin.site.register(Scenario)


class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'source')
    list_filter = ('group',)
    filter_horizontal = ('group',)

admin.site.register(Activity, ActivityAdmin)

admin.site.register(ActivityGroup)

admin.site.register(Answer)


class StudentAdmin(admin.ModelAdmin):
    list_display = ('email', 'scenario', 'current_activity')
admin.site.register(Student, StudentAdmin)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'correct_answer')
    filter_horizontal = ('activity',)
admin.site.register(Question, QuestionAdmin)


class ResultAdmin(admin.ModelAdmin):
    list_display = ('get_email', 'get_activity', 'score')

    def get_email(self, obj):
        return obj.student.email
    get_email.short_description = 'Student'

    def get_activity(self, obj):
        return obj.quiz.name
    get_activity.short_description = 'Activity'
admin.site.register(Result, ResultAdmin)


class ChoiceAdmin(admin.ModelAdmin):
    def get_question(self, obj):
        return obj.question.text
    get_question.short_description = 'Question'
    list_display = ('get_question', 'text')

admin.site.register(Choice, ChoiceAdmin)


class TimeLogAdmin(admin.ModelAdmin):
    list_display = ('get_email', 'get_activity', 'start_time', 'end_time')

    def get_email(self, obj):
        return obj.student.email
    get_email.short_description = 'Student'
        
    def get_activity(self, obj):
        return obj.activity.name
    get_activity.short_description = 'Activity'

admin.site.register(TimeLog, TimeLogAdmin)

