# callanapp/forms.py
from django import forms

# Форма для ввода текста и скорости для создания аудиофайла
class DictationForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'cols': 80}), label='Your Text')
    speed_factor = forms.FloatField(label='Speed Factor', initial=1.0)


# Форма для контактов (получения сообщений)
class ContactForm(forms.Form):
    name = forms.CharField(label='Title')
    email = forms.EmailField(label='Email')
    message = forms.CharField(label='Message')

# Форма для отправки ответных сообщений
class ReplyEmailForm(forms.Form):
    subject = forms.CharField(max_length=200, label='Subject')
    body = forms.CharField(widget=forms.Textarea, label='Body')