from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ForumCategory, ForumTopic, ForumReply

def forum_home(request):
    categories = ForumCategory.objects.filter(is_active=True)
    recent_topics = ForumTopic.objects.all().order_by('-created_at')[:10]
    return render(request, 'community/forum.html', {
        'categories': categories,
        'recent_topics': recent_topics
    })

@login_required
def create_topic(request):
    if request.method == 'POST':
        category_id = request.POST.get('category')
        title = request.POST.get('title')
        content = request.POST.get('content')
        topic = ForumTopic.objects.create(
            category_id=category_id,
            author=request.user,
            title=title,
            content=content
        )
        return redirect('topic_detail', topic_id=topic.id)
    categories = ForumCategory.objects.filter(is_active=True)
    return render(request, 'community/create_topic.html', {'categories': categories})

def topic_detail(request, topic_id):
    topic = get_object_or_404(ForumTopic, id=topic_id)
    topic.view_count += 1
    topic.save()
    replies = topic.replies.all()
    return render(request, 'community/topic.html', {'topic': topic, 'replies': replies})

@login_required
def reply_topic(request, topic_id):
    if request.method == 'POST':
        topic = get_object_or_404(ForumTopic, id=topic_id)
        ForumReply.objects.create(
            topic=topic,
            author=request.user,
            content=request.POST.get('content')
        )
        topic.reply_count += 1
        topic.save()
        return redirect('topic_detail', topic_id=topic_id)
    return redirect('forum_home')
