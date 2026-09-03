from django import forms
from .models import Notice, SocietyPoll, PollOption, DiscussionPost, DiscussionReply, LostAndFoundItem, SocietyDocument

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ('title', 'notice_type', 'content', 'attachment', 'is_pinned', 'target_wings', 'expires_at')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Notice Heading'}),
            'notice_type': forms.Select(attrs={'class': 'form-control form-select'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Detailed announcement text...'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'target_wings': forms.SelectMultiple(attrs={'class': 'form-control', 'size': 3}),
            'expires_at': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class DiscussionPostForm(forms.ModelForm):
    class Meta:
        model = DiscussionPost
        fields = ('title', 'category', 'content', 'image')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Post title or topic'}),
            'category': forms.Select(attrs={'class': 'form-control form-select'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'What would you like to share with the society?'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class DiscussionReplyForm(forms.ModelForm):
    class Meta:
        model = DiscussionReply
        fields = ('message',)
        widgets = {
            'message': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Write a friendly reply...'}),
        }


class LostAndFoundItemForm(forms.ModelForm):
    class Meta:
        model = LostAndFoundItem
        fields = ('item_name', 'category', 'status', 'location', 'description', 'photo', 'contact_phone')
        widgets = {
            'item_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Set of 3 Keys with blue keychain'}),
            'category': forms.Select(attrs={'class': 'form-control form-select'}),
            'status': forms.Select(attrs={'class': 'form-control form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Where was it lost/found? (e.g. Tower A Lift Lobby)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Provide details to help identify the item...'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Phone # for claimant to call'}),
        }


class SocietyDocumentForm(forms.ModelForm):
    class Meta:
        model = SocietyDocument
        fields = ('title', 'category', 'document_file', 'description')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Document Title (e.g. Society Bye-Laws 2026)'}),
            'category': forms.Select(attrs={'class': 'form-control form-select'}),
            'document_file': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
