from .models import News, Commentaries
from django import forms
import re


# class NewsForm(forms.Form):
#     article = forms.CharField()
#     body = forms.CharField(widget=forms.Textarea)

class NewsModelForm(forms.ModelForm):
    class Meta:
        model = News
        fields = [
            'article',
            'body',
            'image',
        ]
    
    def clean_article(self):
        data = self.cleaned_data.get('article')
        if len(data) < 5:
            raise forms.ValidationError('Article is not long enough')
        return data
    
    def clean_body(self):
        data = self.cleaned_data.get('body')
        if 'foo' in re.findall(r'\w+', data):
            raise forms.ValidationError(f'Word foo can not be able in the post!!')
        return data
   
class CommentaryModelForm(forms.ModelForm):
    class Meta:
        model = Commentaries
        fields = [
            'text'
        ] 