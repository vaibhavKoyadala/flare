
from jokermanager import joker_required
from django.core.exceptions import PermissionDenied
from datetime import datetime
from django.http.response import JsonResponse, HttpResponse
from django.http.response import FileResponse
from django.views.decorators.csrf import csrf_exempt
import models
from rest_framework import status
from rest_framework.renderers import JSONRenderer
import serializers

class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

def raise_403(exception):
    raise PermissionDenied()

def unread_messages(joker, fetch_from=None):
    flare = joker.flare
    print fetch_from
    if fetch_from is None:
        messages = models.TextMessage.objects. \
            filter(joker__flare_id__exact=joker.flare.id). \
            order_by('timestamp'). \
            values('text', 'timestamp', 'joker__name')
    else:
        messages = models.TextMessage.objects. \
            filter(joker__flare_id__exact=joker.flare.id). \
            filter(timestamp__gt=fetch_from). \
            order_by('timestamp').\
            values('text', 'timestamp', 'joker__name')
    # Replace the name of the joker to 'self'
    # where sender is the current joker.
    for message in messages:
        name = message['joker__name']
        del message['joker__name']
        message['joker_name'] = 'self' if name == joker.name else name
    return messages

def unread_files(joker, fetch_from=None):
    # TODO: Clean this code
    flare = joker.flare
    print fetch_from
    if fetch_from is None:
        image_messages = models.ImageMessage.objects.\
            filter(joker__flare=flare).\
            order_by('timestamp').\
            values('id', 'size', 'joker__name', 'timestamp', 'title')
        file_messages = models.FileMessage.objects.\
            filter(joker__flare=flare).\
            order_by('timestamp').\
            values('id', 'size', 'joker__name', 'timestamp', 'title')
    else:
        image_messages = models.ImageMessage.objects. \
            filter(joker__flare=flare). \
            filter(timestamp__gt=fetch_from). \
            order_by('timestamp'). \
            values('id', 'size', 'joker__name', 'timestamp', 'title')
        file_messages = models.FileMessage.objects. \
            filter(joker__flare=flare). \
            filter(timestamp__gt=fetch_from). \
            order_by('timestamp'). \
            values('id', 'size', 'joker__name', 'timestamp', 'title')

    # Should contain the following attributes
    # 'url' : url for the actual file
    # 'thumbnail_url' : url for the thumbnail [OPTIONAL]
    # 'timestamp' : timestamp
    # 'joker_name' : name of the joker
    # 'title': title of the file
    # TODO: Clean this code
    for message in image_messages:
        title = message['title']
        name = message['joker__name']
        id = message['id']

        message['url'] = 'api/resource/image/{id}/{title}'.format(id=id, title=title)
        message['thumbnail_url'] = 'api/resource/thumbnail/{id}/{title}'.format(id=id, title=title)
        message['joker_name'] = 'self' if name == joker.name else name

        del message['id']
        del message['joker__name']

    for message in file_messages:
        title = message['title']
        name = message['joker__name']
        id = message['id']

        message['url'] = 'api/resource/other/{id}/{title}'.format(id=id, title=title)
        message['joker_name'] = 'self' if name == joker.name else name

        del message['id']
        del message['joker__name']

    return list(image_messages)+list(file_messages)

@csrf_exempt
@joker_required(on_fail=raise_403)
def fetch_messages(request):
    joker = request.joker
    fetch_from = request.GET.get('fetch_from', None)
    if fetch_from is not None:
        fetch_from = datetime.strptime(fetch_from, r'%Y-%m-%dT%H:%M:%S.%fZ')
        print fetch_from
    messages = unread_messages(joker, fetch_from=fetch_from)
    return JSONResponse(data=messages)

@csrf_exempt
@joker_required(on_fail=raise_403)
def online_jokers(request):
    pass

@csrf_exempt
@joker_required(on_fail=raise_403)
def send_message(request):
    if request.method == 'POST':
        joker = request.joker
        try:

            text = request.POST['text']
            text_message = models.TextMessage(text=text,
                                              joker=joker)
            text_message.save()
            return HttpResponse(content='Sent !')
        except:
            return HttpResponse(str(request.POST))
    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@joker_required(on_fail=raise_403)
def upload(request):
    if 'file' not in request.FILES:
        print 'No file'
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
    file = request.FILES['file']
    file_extension = file.name.rpartition('.')[-1]
    joker = request.joker

    print file_extension
    if file_extension in ['jpeg', 'jpg', 'png']:
        model = models.ImageMessage(joker=joker, image=file, title=file.name)
        model.save()
    else:
        model = models.FileMessage(joker=joker, file=file, title=file.name)
        model.save()
    return HttpResponse('<h1>{0}</h1>'.format(model.title)+
                        '<a href="resource/image/{0}">Image</a>'.format(model.title)+'<br>'+
                        '<a href="resource/thumbnail/{0}">Thumbnail</a>'.format(model.title)+'<br>'+
                        '<a href="resource/other/{0}">Other</a>'.format(model.title))


@csrf_exempt
@joker_required(on_fail=raise_403)
def fetch_files(request):
    joker = request.joker
    fetch_from = request.GET.get('fetch_from', None)
    if fetch_from is not None:
        fetch_from = datetime.strptime(fetch_from, r'%Y-%m-%dT%H:%M:%S.%fZ')
        print fetch_from
    messages = unread_files(joker, fetch_from=fetch_from)
    return JSONResponse(data=messages)


@csrf_exempt
@joker_required(on_fail=raise_403)
def resource(request, type, id, title):
    flare = request.joker.flare
    try:
        if type == 'image':
            file_field = models.ImageMessage.objects.get(pk=id).image
            content_type = 'image/'+file_field.name.rsplit('.', 1)[-1]
        elif type == 'thumbnail':
            file_field = models.ImageMessage.objects.get(pk=id).thumbnail
            content_type = 'image/' + file_field.name.rsplit('.', 1)[-1]
        else:
            file_field = models.FileMessage.objects.get(pk=id).file
            extension = file_field.name.rsplit('.', 1)[-1]
            if extension == 'txt':
                content_type = 'text'
            else:
                content_type = 'application/{0}'.format(extension)
    except:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    return FileResponse(file_field.file, content_type=content_type)

@csrf_exempt
@joker_required(on_fail=raise_403)
def account(request):
    serializer = serializers.JokerSerializer(instance=request.joker)
    print request.joker
    return JSONResponse(data=serializer.data)