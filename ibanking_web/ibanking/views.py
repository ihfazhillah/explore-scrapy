from uuid import uuid4
from django.shortcuts import render
from django.http import JsonResponse
from scrapyd_api import ScrapydAPI

from .models import ScrapyItem

# Create your views here.

scrapyd = ScrapydAPI('http://localhost:6800')


def get_statements(request):
    unique_id = str(uuid4())

    settings = {
        'unique_id': unique_id
    }

    task = scrapyd.schedule('default', 'ibmandiri', settings=settings, to_crawl='otjlsjflask')

    return JsonResponse({
        'task_id': task,
        'unique_id': unique_id,
        'status': 'started',
        'url': '/check_job?unique_id={}&task_id={}'.format(unique_id, task)
    })


def check_job_get_statements(request):
    task_id = request.GET.get('task_id')
    unique_id = request.GET.get('unique_id')

    status = scrapyd.job_status('default', task_id)
    if status == 'finished':
        item = ScrapyItem.objects.get(unique_id=unique_id)
        return JsonResponse(item.to_dict())
    return JsonResponse({'status': status})

