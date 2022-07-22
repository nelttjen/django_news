from django import forms

from .models import Tag


class TagSelectionForm(forms.Form):
    categories = forms.ModelMultipleChoiceField(Tag.objects, required=False, label=False,
                                                widget=forms.CheckboxSelectMultiple(attrs={'class': 'tag_checkbox'}))


class SearchForm(TagSelectionForm):
    search = forms.CharField(label=None,
                             widget=forms.TextInput(attrs={'class': 'form-control',
                                                           'placeholder': 'Поиск по новостям'}),
                             required=False
                             )

    field_order = ['search', 'categories']


class PostForm(TagSelectionForm):
    title = forms.CharField(label='Название новости',
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название'}),
                            min_length=3, max_length=200)
    content = forms.CharField(label='Содержание новости',
                              widget=forms.Textarea(attrs={'class': 'form-control',
                                                           'placeholder': 'Введите содержание новости'}),
                              min_length=10, max_length=3000)
    image = forms.ImageField(label='Картинка (Необязательно)',
                             widget=forms.FileInput(attrs={'class': 'form-control'}),
                             required=False)

    field_order = ['title', 'content', 'image', 'categories']
