# -*- coding: utf-8 -*-

from WeChatTicket import settings
from wechat.wrapper import WeChatHandler
from wechat.models import Activity, Ticket
import uuid

__author__ = "Epsirom"


class ErrorHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，服务器现在有点忙，暂时不能给您答复 T T')


class DefaultHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，没有找到您需要的信息:(')


class HelpOrSubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('帮助', 'help') or self.is_event('scan', 'subscribe') or \
               self.is_event_click(self.view.event_keys['help'])

    def handle(self):
        return self.reply_single_news({
            'Title': self.get_message('help_title'),
            'Description': self.get_message('help_description'),
            'Url': self.url_help(),
        })


class UnbindOrUnsubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('解绑') or self.is_event('unsubscribe')

    def handle(self):
        self.user.student_id = ''
        self.user.save()
        return self.reply_text(self.get_message('unbind_account'))


class BindAccountHandler(WeChatHandler):

    def check(self):
        return self.is_text('绑定') or self.is_event_click(self.view.event_keys['account_bind'])

    def handle(self):
        return self.reply_text(self.get_message('bind_account'))


class BookWhatHandler(WeChatHandler):

    def check(self):
        return self.is_text('抢啥') or self.is_event_click(self.view.event_keys['book_what'])

    def handle(self):
        articles = []
        if self.user.student_id:
            available_articles = Activity.objects.filter(status=Activity.STATUS_PUBLISHED)
            for i in available_articles:
                articles.append({
                    'Title': '活动：%s' % i.name,
                    'Description': i.description,
                    'PicUrl': i.pic_url,
                    'Url': settings.get_url('u/activity', {'id': i.id})
                })
            return self.reply_news(articles=articles)
        return self.reply_text(self.get_message('bind_account'))


class GetTicketHandler(WeChatHandler):

    def check(self):
        return self.is_text('查票') or self.is_event_click(self.view.event_keys['get_ticket'])

    def handle(self):
        articles = []
        if self.user.student_id:
            available_articles = Ticket.objects.filter(student_id=self.user.student_id)
            for i in available_articles:
                articles.append({
                    'Title': '票：%s' % i.activity.name,
                    'Description': i.activity.description,
                    'PicUrl': i.activity.pic_url,
                    'Url': settings.get_url('u/ticket', {'openid': self.user.open_id, 'ticket': i.unique_id})
                })
            return self.reply_news(articles=articles)
        return self.reply_text(self.get_message('bind_account'))


class BookHandler(WeChatHandler):

    def check(self):
        return self.is_text_command('抢票')

    def handle(self):
        activity_key = self.input['Content'][3:]
        if self.user.student_id:
            activities = Activity.objects.filter(key=activity_key)
            if len(activities) == 1 and activities[0].remain_tickets > 0:
                activities[0].remain_tickets -= 1
                Ticket.objects.create(unique_id=str(uuid.uuid4()),
                                      student_id=self.user.student_id,
                                      activity=activities[0],
                                      status=Ticket.STATUS_VALID)
                return self.reply_text('抢票成功')
            return self.reply_text('抢票失败')
        return self.reply_text(self.get_message('bind_account'))


class RefundHandler(WeChatHandler):

    def check(self):
        return self.is_text_command('退票')

    def handle(self):
        activity_key = self.input['Content'][3:]
        if self.user.student_id:
            activities = Activity.objects.filter(key=activity_key)
            if len(activities) == 1 and activities[0].remain_tickets > 0:
                activities[0].remain_tickets -= 1
                tickets = Ticket.objects.filter(activity=activities[0],
                                          student_id=self.user.student_id,
                                          status=Ticket.STATUS_VALID)
                if len(tickets) == 1:
                    tickets[0].status = Ticket.STATUS_CANCELLED
                    tickets[0].activity.remain_tickets += 1
                    tickets[0].activity.save()
                    tickets[0].save()
                    return self.reply_text('退票成功')
            return self.reply_text('不存在未使用的票')
        return self.reply_text(self.get_message('bind_account'))


class GetSingleTicketHandler(WeChatHandler):

    def check(self):
        return self.is_text_command('取票')

    def handle(self):
        activity_key = self.input['Content'][3:]
        if self.user.student_id:
            activities = Activity.objects.filter(key=activity_key)
            if len(activities) == 1 and activities[0].remain_tickets > 0:
                activities[0].remain_tickets -= 1
                tickets = Ticket.objects.filter(activity=activities[0],
                                          student_id=self.user.student_id,
                                          status=Ticket.STATUS_VALID)
                if len(tickets) == 1:
                    i = tickets[0]
                    article = {
                        'Title': '票：%s' % i.activity.name,
                        'Description': i.activity.description,
                        'PicUrl': i.activity.pic_url,
                        'Url': settings.get_url('u/ticket', {'openid': self.user.open_id, 'ticket': i.unique_id})
                    }
                    return self.reply_single_news(article=article)
            return self.reply_text('不存在未使用的票')
        return self.reply_text(self.get_message('bind_account'))


class BookEmptyHandler(WeChatHandler):

    def check(self):
        return self.is_event_click(self.view.event_keys['book_empty'])

    def handle(self):
        return self.reply_text(self.get_message('book_empty'))
