from django import forms
from .models import Category

categories = Category.objects.all()
select_category = [(category.name, category.name) for category in categories]


class ListingForm(forms.Form):
    title = forms.CharField(label="Title", max_length=100)
    description = forms.CharField(label='Description', max_length=255, widget=forms.Textarea(attrs={'rows': 5}))
    starting_bid = forms.IntegerField(label='Staring bid')
    image_url = forms.URLField(label='Image Url', required=False)
    category = forms.ChoiceField(label='Choose category', choices=select_category)
    def __init__(self, *args, **kwargs):
        super(ListingForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

            
class CommentForm(forms.Form):
    content = forms.CharField(label='', max_length=100)

class BidForm(forms.Form):
    amount = forms.IntegerField(label='')