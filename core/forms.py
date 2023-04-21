from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea(attrs={'rows':3}))

    class Meta:
        model = Message
        fields =['message']