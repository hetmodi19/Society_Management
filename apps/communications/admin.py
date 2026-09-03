from django.contrib import admin
from .models import Notice, SocietyPoll, PollOption, PollVote, DiscussionPost, DiscussionReply

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'notice_type', 'author', 'is_pinned', 'is_active', 'created_at')
    list_filter = ('notice_type', 'is_pinned', 'is_active')
    search_fields = ('title', 'content')

class PollOptionInline(admin.TabularInline):
    model = PollOption
    extra = 2

@admin.register(SocietyPoll)
class SocietyPollAdmin(admin.ModelAdmin):
    list_display = ('question', 'created_by', 'is_active', 'end_date', 'total_votes', 'created_at')
    inlines = [PollOptionInline]

@admin.register(DiscussionPost)
class DiscussionPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'replies_count', 'created_at')
    list_filter = ('category', 'is_pinned')

@admin.register(DiscussionReply)
class DiscussionReplyAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at')
