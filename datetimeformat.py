# -*- coding: utf-8 -*-

def datetimeformat(value):
    weekday = (u"星期一",u"星期二",u"星期三",u"星期四",u"星期五",u"星期六",u"星期日",)
    return u"%s %s年%s月%s日" % (weekday[value.weekday()],value.year,value.month,value.day)
