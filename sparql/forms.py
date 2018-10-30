from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class QueryForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.Textarea()
    )

    def __init__(self, *args, **kwargs):
        super(QueryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.form_class = 'form-horizontal'
