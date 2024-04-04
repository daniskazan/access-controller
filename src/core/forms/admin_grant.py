from django import forms


class ActivateGrantForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    db_url = forms.CharField(required=True)
    command = forms.CharField(
        label="Найдите шаблон команды в таблице скриптов и измените его здесь",
        required=True,
        widget=forms.Textarea,
    )
