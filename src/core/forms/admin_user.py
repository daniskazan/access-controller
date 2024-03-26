from django import forms

time_widget = forms.widgets.TimeInput(attrs={"type": "time"})
valid_time_formats = ["%P", "%H:%M%A", "%H:%M %A", "%H:%M%a", "%H:%M %a"]


class SendMessageForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)

    message = forms.CharField(widget=forms.Textarea, label="Отправить сообщение")
