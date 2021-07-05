from django import forms
from django.forms import ModelForm
from django.forms.widgets import HiddenInput
from auctions import models
from django.utils.translation import ugettext_lazy as _


class ListingForm(ModelForm):
    class Meta:
        model = models.Listing
        fields = ['title', 'description',  'starting_bid', 'image_url','category']
        widgets = {
            'description': forms.Textarea(),
            'bid_count': HiddenInput(),
            'active': HiddenInput(),
        }
        labels = {
            'starting_bid': _('Starting Bid ($):'),
            'image_url': _('Image URL (optional):'),
            'category': _('Category (optional):'),
        }


class BidForm(ModelForm):
    class Meta:
        model = models.Bid
        fields = ['value']
        labels = {
            'value': _('Bid Value ($):'),
        }

class CommentForm(ModelForm):
    class Meta:
        model = models.Comment
        fields = ['value']
        widgets = {
            'value': forms.Textarea(),
        }
        labels = {
            'value': _('')
        }