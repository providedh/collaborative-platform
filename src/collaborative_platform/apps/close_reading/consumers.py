from channels import Group
from channels.sessions import channel_session
from channels.auth import channel_session_user, channel_session_user_from_http

# from models import ZawartoscXml
#
# from channels_presence.models import Room
# from channels_presence.decorators import touch_presence

from channels.asgi import get_channel_layer
from django.db import models


# class RoomWithXML(Room):
#     tresc = models.TextField()


@channel_session_user_from_http
def ws_connect(message):
    Group('stocks').add(message.reply_channel)

    # Room.objects.add('stocks', message.reply_channel.name, message.user)

    Group('stocks').send({'text': 'connected'})


# @touch_presence
@channel_session_user
def ws_message(message):
    # obiekt_w_bazie = ZawartoscXml.objects.get(moje_id='1234')

    grupa = Group('stocks')
    grupa.moje_pole = 'lalala'

    # if not obiekt_w_bazie:
    #     obiekt_w_bazie = ZawartoscXml(moje_id='1234', tresc='lalala')
    #     obiekt_w_bazie.save()

    wyslany_tekst = message.content['text']
    Group('stocks').send({'text': wyslany_tekst})

    # message.channel_session.myobject = {'test': True}

    # if 'klucz' not in message.channel_session:
    #     message.channel_session['klucz'] = ''

    print(wyslany_tekst)
    # print(message.channel_session['klucz'])

    # stary_tekst = obiekt_w_bazie.tresc
    #
    # nowy_tekst = stary_tekst + wyslany_tekst
    #
    # obiekt_w_bazie.tresc = nowy_tekst
    # obiekt_w_bazie.save()

    # Group('stocks').send({'text': obiekt_w_bazie.tresc})
    #
    # room = Room.objects.get(channel_name='stocks')
    # userzy = room.get_anonymous_count()

    # room.

    # channel_layer = get_channel_layer()
    # userzy_2 = channel_layer.group_channels('stocks')


    do_testow = 0
    pass


@channel_session_user
def ws_disconnect(message):
    Group('stocks').send({'text': 'disconnected'})
    Group('stocks').discard(message.reply_channel)
    # Room.objects.remove('stocks', message.reply_channel.name)
