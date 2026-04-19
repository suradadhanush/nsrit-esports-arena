"""Players - Forms"""
from django import forms
from .models import Player


class PlayerProfileForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['ign', 'game_id', 'primary_game', 'secondary_game', 'bio', 'discord_id', 'instagram_handle', 'is_available']
        widgets = {
            'ign': forms.TextInput(attrs={'class': 'form-control cyber-input', 'placeholder': 'Your In-Game Name'}),
            'game_id': forms.TextInput(attrs={'class': 'form-control cyber-input', 'placeholder': 'Game UID / ID'}),
            'primary_game': forms.Select(attrs={'class': 'form-select cyber-select'}),
            'secondary_game': forms.Select(attrs={'class': 'form-select cyber-select'}),
            'bio': forms.Textarea(attrs={'class': 'form-control cyber-input', 'rows': 3, 'placeholder': 'Tell the arena about yourself...'}),
            'discord_id': forms.TextInput(attrs={'class': 'form-control cyber-input', 'placeholder': 'username#0000'}),
            'instagram_handle': forms.TextInput(attrs={'class': 'form-control cyber-input', 'placeholder': '@handle'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
