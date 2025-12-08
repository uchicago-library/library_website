from django import forms


class EmailNotificationTestForm(forms.Form):
    email_from = forms.EmailField(label="From email address:")
    email_to = forms.EmailField(label="To email address:")
    num_days = forms.IntegerField(label="Number of days of news stories to summarize:")
    email_as_if_date = forms.DateField(
        label="Send the message as if it were the following date. (Use YYYY-MM-DD format.)"
    )
