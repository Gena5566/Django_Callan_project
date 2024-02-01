# admin.py
from django.contrib import admin
from .models import Word, AudioDictation, SentEmail
from django.urls import reverse
from django.utils.html import format_html

# Регистрация моделей в админ-панели Django

# Регистрация модели Word
admin.site.register(Word)

# Регистрация модели AudioDictation
admin.site.register(AudioDictation)


# Регистрация модели SentEmail для отправки уведомлений пользователем и ответа на сообщения из админ-панели
@admin.register(SentEmail)
class SentEmailAdmin(admin.ModelAdmin):
    list_display = ['subject', 'sent_at', 'sender', 'recipient', 'reply_link']
    search_fields = ['subject', 'body', 'sender', 'recipient']

    def reply_link(self, obj):
        return format_html('<a href="{}">Reply</a>', reverse('admin_sentemail_reply', args=[obj.id]))

    reply_link.short_description = 'Reply'


