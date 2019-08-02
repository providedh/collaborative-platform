from channels import Group
from channels.sessions import channel_session
from channels.auth import channel_session_user, channel_session_user_from_http
import json
# from src.collaborative_platform.apps.close_reading.models import AnnotatingXmlContent
# from ..files_management.models import File


# from models import ZawartoscXml
#
from channels_presence.models import Room
from channels_presence.decorators import touch_presence

from channels.asgi import get_channel_layer
# from django.db import models
# from ..close_reading.models import AnnotatingXmlContent
from apps.close_reading.models import AnnotatingXmlContent
from apps.files_management.models import FileVersion
from apps.projects.models import Contributor, Project
from .annotator import Annotator, NotModifiedException


# class RoomWithXML(Room):
#     tresc = models.TextField()



@channel_session_user_from_http
def ws_connect(message):
    room_symbol = get_room_symbol(message)
    project_id, file_id = room_symbol.split('_')

    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        response = {
            'status': 404,
            'message': "Project with id: {} doesn't exist.".format(project_id),
            'xml_content': None,
        }

        response = json.dumps(response)
        message.reply_channel.send({'text': response})

    contributor = Contributor.objects.filter(project_id=project_id, user_id=message.user.pk)
    if not contributor:
        response = {
            'status': 403,
            'message': "You aren't contributor in project with id: {}.".format(project_id),
            'xml_content': None,
        }

        response = json.dumps(response)
        message.reply_channel.send({'text': response})

    try:
        annotating_xml_content = AnnotatingXmlContent.objects.get(file_symbol=room_symbol)

    except AnnotatingXmlContent.DoesNotExist:
        try:
            file = FileVersion.objects.filter(file_id=file_id).order_by('-number')[0]
        except FileVersion.DoesNotExist:
            response = {
                'status': 404,
                'message': 'File not foud.',
                'xml_content': None,
            }

            response = json.dumps(response)
            message.reply_channel.send({'text': response})
            return

        with open(file.upload.path) as file:
            xml_content = file.read()

            annotating_xml_content = AnnotatingXmlContent(file_symbol=room_symbol, xml_content=xml_content)
            annotating_xml_content.save()

    Group(room_symbol).add(message.reply_channel)
    Room.objects.add(room_symbol, message.reply_channel.name, message.user)

    response = {
        'status': 200,
        'message': 'OK',
        'xml_content': annotating_xml_content.xml_content,
    }

    response = json.dumps(response)
    message.reply_channel.send({'text': response})


@touch_presence
@channel_session_user
def ws_message(message):
    room_symbol = get_room_symbol(message)
    request_json = message.content['text']

    annotating_xml_content = AnnotatingXmlContent.objects.get(file_symbol=room_symbol)
    xml_content = annotating_xml_content.xml_content
    request_json = json.loads(request_json)
    user_id = message.user.pk

    print("REQUEST JSON:\n{}".format(request_json))

    try:
        annotator = Annotator()
        xml_content = annotator.add_annotation(xml_content, request_json, user_id)

        annotating_xml_content.xml_content = xml_content
        annotating_xml_content.save()

        print("ODPOWIEDZ:\n{}".format(annotating_xml_content.xml_content))

        response = {
            'status': 200,
            'message': 'OK',
            'xml_content': annotating_xml_content.xml_content,
        }

        response = json.dumps(response)
        Group(room_symbol).send({'text': response})

    except NotModifiedException as exception:
        response = {
            'status': 304,
            'message': str(exception),
            'xml_content': None,
        }

        print("ODPOWIEDZ:\n{}".format(response))

        response = json.dumps(response)
        message.reply_channel.send({'text': response})

    except (ValueError, TypeError) as error:
        response = {
            'status': 400,
            'message': error.message,
            'xml_content': None,
        }

        print("ODPOWIEDZ:\n{}".format(response))

        response = json.dumps(response)
        message.reply_channel.send({'text': response})


@channel_session_user
def ws_disconnect(message):
    room_symbol = get_room_symbol(message)

    room = Room.objects.get(channel_name=room_symbol)
    users_connected = len(room.get_users())
    # users_connected = room.get_anonymous_count()

    if users_connected < 2:
        annotating_xml_content = AnnotatingXmlContent.objects.get(file_symbol=room_symbol)
        annotating_xml_content.delete()

    Group(room_symbol).discard(message.reply_channel)
    Room.objects.remove(room_symbol, message.reply_channel.name)


def get_room_symbol(message):
    room_symbol = message['path'].strip('/').split('/')[-1]

    return room_symbol
