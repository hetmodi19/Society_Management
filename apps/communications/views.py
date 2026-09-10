from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

from .models import Notice, SocietyPoll, PollOption, PollVote, DiscussionPost, DiscussionReply, LostAndFoundItem, SocietyDocument
from .forms import NoticeForm, DiscussionPostForm, DiscussionReplyForm, LostAndFoundItemForm, SocietyDocumentForm

@login_required
def notices_list_view(request):
    """View active circulars and pinned society notices."""
    notices = Notice.objects.filter(is_active=True).select_related('author')
    type_filter = request.GET.get('type', '')
    search_query = request.GET.get('q', '').strip()

    if type_filter:
        notices = notices.filter(notice_type=type_filter)
    if search_query:
        notices = notices.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    return render(request, 'communications/notices_list.html', {
        'notices': notices,
        'selected_type': type_filter,
        'search_query': search_query,
    })


@login_required
def notice_detail_view(request, pk):
    """View full notice announcement."""
    notice = get_object_or_404(Notice.objects.select_related('author'), pk=pk)
    return render(request, 'communications/notice_detail.html', {'notice': notice})


@login_required
def create_notice_view(request):
    """Create a new official circular."""
    if not (request.user.is_society_admin or request.user.is_committee_member):
        messages.error(request, "Permission denied. Only committee members can publish circulars.")
        return redirect('communications:notices')

    if request.method == 'POST':
        form = NoticeForm(request.POST, request.FILES)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.author = request.user
            notice.save()
            form.save_m2m()
            messages.success(request, f"Notice '{notice.title}' published successfully!")
            return redirect('communications:notices')
    else:
        form = NoticeForm()

    return render(request, 'communications/create_notice.html', {'form': form})


@login_required
def polls_list_view(request):
    """Browse democratic society polls with live percentage results."""
    polls = SocietyPoll.objects.prefetch_related('options', 'votes', 'created_by').all()
    user_votes = PollVote.objects.filter(user=request.user).values_list('poll_id', 'option_id')
    user_voted_map = {p_id: opt_id for p_id, opt_id in user_votes}

    return render(request, 'communications/polls_list.html', {
        'polls': polls,
        'user_voted_map': user_voted_map,
    })


@login_required
def vote_poll_view(request, pk):
    """Cast a resident vote on an active poll."""
    poll = get_object_or_404(SocietyPoll, pk=pk)
    if poll.is_closed:
        messages.error(request, "This poll is closed for voting.")
        return redirect('communications:polls')

    if poll.user_has_voted(request.user):
        messages.warning(request, "You have already cast your vote in this poll.")
        return redirect('communications:polls')

    option_id = request.POST.get('option_id')
    if not option_id:
        messages.error(request, "Please select an option to vote.")
        return redirect('communications:polls')

    option = get_object_or_404(PollOption, pk=option_id, poll=poll)
    PollVote.objects.create(poll=poll, option=option, user=request.user)
    messages.success(request, f"Your vote for '{option.option_text}' has been recorded!")
    return redirect('communications:polls')


@login_required
def create_poll_view(request):
    """Create a new society poll with customizable options."""
    if not (request.user.is_society_admin or request.user.is_committee_member):
        messages.error(request, "Only committee members can initiate society polls.")
        return redirect('communications:polls')

    if request.method == 'POST':
        question = request.POST.get('question', '').strip()
        description = request.POST.get('description', '').strip()
        days = int(request.POST.get('duration_days', 7))
        options_raw = request.POST.getlist('options')

        if question and options_raw:
            poll = SocietyPoll.objects.create(
                question=question,
                description=description,
                created_by=request.user,
                end_date=timezone.now().date() + timedelta(days=days)
            )
            for opt_text in options_raw:
                if opt_text.strip():
                    PollOption.objects.create(poll=poll, option_text=opt_text.strip())

            messages.success(request, f"Society Poll '{poll.question}' created successfully!")
            return redirect('communications:polls')
        else:
            messages.error(request, "Please provide a question and at least two options.")

    return render(request, 'communications/create_poll.html')


@login_required
def forum_list_view(request):
    """Community discussion feed and classifieds."""
    posts = DiscussionPost.objects.select_related('author').prefetch_related('replies')
    category_filter = request.GET.get('category', '')

    if category_filter:
        posts = posts.filter(category=category_filter)

    form = DiscussionPostForm()
    return render(request, 'communications/forum_list.html', {
        'posts': posts,
        'form': form,
        'selected_category': category_filter,
    })


@login_required
def create_post_view(request):
    """Create a new forum topic or buy/sell item."""
    if request.method == 'POST':
        form = DiscussionPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, f"Discussion post '{post.title}' published!")
            return redirect('communications:post_detail', pk=post.pk)
    return redirect('communications:forum')


@login_required
def post_detail_view(request, pk):
    """Discussion thread view with conversational replies."""
    post = get_object_or_404(DiscussionPost.objects.select_related('author'), pk=pk)

    if request.method == 'POST':
        reply_form = DiscussionReplyForm(request.POST)
        if reply_form.is_valid():
            reply = reply_form.save(commit=False)
            reply.post = post
            reply.author = request.user
            reply.save()
            messages.success(request, "Reply added to discussion.")
            return redirect('communications:post_detail', pk=post.pk)
    else:
        reply_form = DiscussionReplyForm()

    replies = post.replies.select_related('author').all()

    return render(request, 'communications/post_detail.html', {
        'post': post,
        'replies': replies,
        'reply_form': reply_form,
    })


@login_required
def lost_found_view(request):
    """Lost & Found Community Hub."""
    items = LostAndFoundItem.objects.select_related('reported_by').all()
    status_filter = request.GET.get('status', '')

    if status_filter:
        items = items.filter(status=status_filter)

    if request.method == 'POST':
        form = LostAndFoundItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.reported_by = request.user
            item.save()
            messages.success(request, f"Item '{item.item_name}' logged in Lost & Found Hub!")
            return redirect('communications:lost_found')
    else:
        form = LostAndFoundItemForm()

    return render(request, 'communications/lost_found.html', {
        'items': items,
        'form': form,
        'selected_status': status_filter,
    })


@login_required
def claim_item_view(request, pk):
    """Mark a lost/found item as claimed."""
    item = get_object_or_404(LostAndFoundItem, pk=pk)
    item.status = LostAndFoundItem.ItemStatus.CLAIMED
    item.save()
    messages.success(request, f"'{item.item_name}' has been marked as Claimed / Returned.")
    return redirect('communications:lost_found')


@login_required
def documents_vault_view(request):
    """Society Document, Bye-Laws & Meeting Minutes Vault."""
    docs = SocietyDocument.objects.all()
    category_filter = request.GET.get('category', '')

    if category_filter:
        docs = docs.filter(category=category_filter)

    if request.method == 'POST':
        if not (request.user.is_society_admin or request.user.is_committee_member):
            messages.error(request, "Only committee members can upload official documents.")
            return redirect('communications:documents')

        form = SocietyDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.uploaded_by = request.user
            doc.save()
            messages.success(request, f"Document '{doc.title}' uploaded to Society Vault!")
            return redirect('communications:documents')
    else:
        form = SocietyDocumentForm()

    return render(request, 'communications/documents.html', {
        'docs': docs,
        'form': form,
        'selected_category': category_filter,
    })


@login_required
def delete_notice_view(request, pk):
    """Delete a notice / circular (Author or Admin/Committee)."""
    notice = get_object_or_404(Notice, pk=pk)
    if not (request.user.is_society_admin or request.user.is_committee_member or notice.author == request.user):
        messages.error(request, "Permission Denied: Only Admin/Committee can delete notices.")
        return redirect('communications:notices')

    if request.method == 'POST':
        title = notice.title
        notice.delete()
        messages.success(request, f"Notice '{title}' has been deleted.")
        return redirect('communications:notices')
    return redirect('communications:notice_detail', pk=notice.pk)


@login_required
def delete_poll_view(request, pk):
    """Delete a society poll (Creator or Admin/Committee)."""
    poll = get_object_or_404(SocietyPoll, pk=pk)
    if not (request.user.is_society_admin or request.user.is_committee_member or poll.created_by == request.user):
        messages.error(request, "Permission Denied: You cannot delete this poll.")
        return redirect('communications:polls')

    if request.method == 'POST':
        q = poll.question
        poll.delete()
        messages.success(request, f"Poll '{q}' has been removed.")
        return redirect('communications:polls')
    return redirect('communications:polls')


@login_required
def delete_post_view(request, pk):
    """Delete a community forum discussion post (Author or Admin/Committee)."""
    post = get_object_or_404(DiscussionPost, pk=pk)
    if not (request.user.is_society_admin or request.user.is_committee_member or post.author == request.user):
        messages.error(request, "Permission Denied: You cannot delete this post.")
        return redirect('communications:forum')

    if request.method == 'POST':
        title = post.title
        post.delete()
        messages.success(request, f"Discussion post '{title}' has been deleted.")
        return redirect('communications:forum')
    return redirect('communications:post_detail', pk=post.pk)


@login_required
def delete_reply_view(request, pk):
    """Delete a discussion reply."""
    reply = get_object_or_404(DiscussionReply, pk=pk)
    post_pk = reply.post.pk
    if not (request.user.is_society_admin or request.user.is_committee_member or reply.author == request.user):
        messages.error(request, "Permission Denied: You cannot delete this reply.")
        return redirect('communications:post_detail', pk=post_pk)

    if request.method == 'POST':
        reply.delete()
        messages.success(request, "Reply deleted.")
        return redirect('communications:post_detail', pk=post_pk)
    return redirect('communications:post_detail', pk=post_pk)


@login_required
def delete_lost_found_view(request, pk):
    """Delete a lost and found listing."""
    item = get_object_or_404(LostAndFoundItem, pk=pk)
    if not (request.user.is_society_admin or request.user.is_committee_member or item.reported_by == request.user):
        messages.error(request, "Permission Denied: You cannot delete this item.")
        return redirect('communications:lost_found')

    if request.method == 'POST':
        name = item.item_name
        item.delete()
        messages.success(request, f"Lost & Found item '{name}' has been deleted.")
        return redirect('communications:lost_found')
    return redirect('communications:lost_found')


@login_required
def delete_document_view(request, pk):
    """Delete a document from society vault (Admin/Committee only)."""
    doc = get_object_or_404(SocietyDocument, pk=pk)
    if not (request.user.is_society_admin or request.user.is_committee_member):
        messages.error(request, "Permission Denied: Only Admin/Committee can delete documents.")
        return redirect('communications:documents')

    if request.method == 'POST':
        title = doc.title
        doc.delete()
        messages.success(request, f"Document '{title}' has been deleted from the vault.")
        return redirect('communications:documents')
    return redirect('communications:documents')

