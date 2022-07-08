from django import forms

from .models import Tag


class TagSelectionForm(forms.Form):
    categories = forms.ModelMultipleChoiceField(Tag.objects, required=False, label=False,
                                                widget=forms.CheckboxSelectMultiple(attrs={'class': 'tag_checkbox'}))


class PostForm(forms.Form):
    title = forms.CharField(label='Название новости',
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название'}),
                            min_length=3)
    content = forms.CharField(label='Содержание новости',
                              widget=forms.Textarea(attrs={'class': 'form-control',
                                                           'placeholder': 'Введите содержание новости'}),
                              min_length=10)
    image = forms.ImageField(label='Картинка (Необязательно)',
                             widget=forms.FileInput(attrs={'class': 'form-control'}),
                             required=False)
    categories = forms.ModelMultipleChoiceField(Tag.objects, required=False, label='Выберите категории (Необязательно)',
                                                widget=forms.CheckboxSelectMultiple(attrs={'class': 'tag_checkbox'}))
