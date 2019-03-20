from django import forms
from django_countries.widgets import CountrySelectWidget
from identity.models import Service


class ServiceMetadataForm(forms.ModelForm):
	class Meta:
		model = Service
		fields = ('country_of_origin', 'sector')
		# widgets = {'country_of_origin': CountrySelectWidget(layout='<div class="input-group-prepend"><span class="input-group-addon"><img class="country-select-flag" id="{flag_id}" style="margin: 6px 4px 0" src="{country.flag}"></span></div>{widget}')}
		widgets = {'country_of_origin': CountrySelectWidget(layout='{widget}')}
