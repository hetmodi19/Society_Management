from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Notice(models.Model):
    class NoticeType(models.TextChoices):
        GENERAL = 'GENERAL', _('General Circular / Announcement')
        URGENT = 'URGENT', _('Urgent Alert / Warning')
        AGM = 'AGM', _('AGM / General Body Meeting')
        MAINTENANCE = 'MAINTENANCE', _('Water / Power Shutdown Notice')
        EVENT = 'EVENT', _('Festival & Cultural Celebration')
        FINANCIAL = 'FINANCIAL', _('Audited Accounts & Budget Report')

    title = models.CharField(max_length=200)
    notice_type = models.CharField(max_length=30, choices=NoticeType.choices, default=NoticeType.GENERAL)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='published_notices')
    content = models.TextField()
    attachment = models.FileField(upload_to='notices/docs/', blank=True, null=True)
    is_pinned = models.BooleanField(default=False, help_text=_("Pin to top of dashboards"))
    is_active = models.BooleanField(default=True)
    target_wings = models.ManyToManyField('properties.Wing', blank=True, help_text=_("Leave blank for entire society broadcast"))
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return f"[{self.get_notice_type_display()}] {self.title}"


class SocietyPoll(models.Model):
    question = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_polls')
    is_active = models.BooleanField(default=True)
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.question

    @property
    def total_votes(self):
        return self.votes.count()

    @property
    def is_closed(self):
        return not self.is_active or timezone.now().date() > self.end_date

    def user_has_voted(self, user):
        if not user.is_authenticated:
            return False
        return self.votes.filter(user=user).exists()


class PollOption(models.Model):
    poll = models.ForeignKey(SocietyPoll, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.poll.question[:30]}... -> {self.option_text}"

    @property
    def votes_count(self):
        return self.votes.count()

    @property
    def percentage(self):
        total = self.poll.total_votes
        if total == 0:
            return 0
        return round((self.votes_count / total) * 100, 1)


class PollVote(models.Model):
    poll = models.ForeignKey(SocietyPoll, on_delete=models.CASCADE, related_name='votes')
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='poll_votes')
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('poll', 'user')

    def __str__(self):
        return f"{self.user.username} voted on {self.poll.question}"


class DiscussionPost(models.Model):
    class Category(models.TextChoices):
        GENERAL = 'GENERAL', _('General Chit-Chat')
        BUY_SELL = 'BUY_SELL', _('Buy & Sell / Marketplace')
        EVENT = 'EVENT', _('Community Events & Meetups')
        RECOMMEND = 'RECOMMEND', _('Recommendations & Reviews')

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=30, choices=Category.choices, default=Category.GENERAL)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_posts')
    content = models.TextField()
    image = models.ImageField(upload_to='forum/images/', blank=True, null=True)
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return f"{self.title} by {self.author.full_name}"

    @property
    def replies_count(self):
        return self.replies.count()


class DiscussionReply(models.Model):
    post = models.ForeignKey(DiscussionPost, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Reply by {self.author.full_name} on {self.post.title}"


class LostAndFoundItem(models.Model):
    class ItemStatus(models.TextChoices):
        LOST = 'LOST', _('Lost Item')
        FOUND = 'FOUND', _('Found Item')
        CLAIMED = 'CLAIMED', _('Claimed / Returned')

    class Category(models.TextChoices):
        KEYS = 'KEYS', _('Keys & FOBs')
        ELECTRONICS = 'ELECTRONICS', _('Phones, Earbuds & Tech')
        PETS = 'PETS', _('Lost / Rescued Pets')
        DOCUMENTS = 'DOCUMENTS', _('Cards, Wallets & IDs')
        TOYS = 'TOYS', _('Children Toys & Cycles')
        ACCESSORIES = 'ACCESSORIES', _('Watches, Glasses & Apparel')
        OTHER = 'OTHER', _('Other Belonging')

    item_name = models.CharField(max_length=150)
    category = models.CharField(max_length=30, choices=Category.choices, default=Category.KEYS)
    status = models.CharField(max_length=20, choices=ItemStatus.choices, default=ItemStatus.FOUND)
    location = models.CharField(max_length=150, help_text=_("e.g. Garden Bench near Tower B, Clubhouse Gym"))
    description = models.TextField()
    photo = models.ImageField(upload_to='lost_found/', blank=True, null=True)
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reported_items')
    contact_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_status_display()}] {self.item_name} @ {self.location}"


class SocietyDocument(models.Model):
    class Category(models.TextChoices):
        BYELAWS = 'BYELAWS', _('Society Bye-Laws & Rules')
        AGM_MINUTES = 'AGM_MINUTES', _('AGM / SGM Meeting Minutes')
        FINANCIAL = 'FINANCIAL', _('Audited Annual Balance Sheet')
        FIRE_NOC = 'FIRE_NOC', _('Fire Safety & Municipal NOC')
        FITOUT = 'FITOUT', _('Renovation & Fit-out Guidelines')
        OTHER = 'OTHER', _('General Society Policy')

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=30, choices=Category.choices, default=Category.BYELAWS)
    document_file = models.FileField(upload_to='society_docs/', blank=True, null=True)
    file_size_text = models.CharField(max_length=20, default='1.2 MB PDF')
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', '-uploaded_at']

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"
