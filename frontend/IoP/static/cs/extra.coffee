get_notification_messages = () ->
  request = $.ajax
    url: '/get/notification/message/names'
    method: 'POST'
    data: {}

  request.done (msg) ->
    msg = JSON.parse msg
    $('.dropdown.notification_message > .menu').emtpy
    for message in msg['result']

      uuid = message['uuid']
      name = message['name']

      tag = "<div class='item' data-value='#{uuid}'>#{name}</div>"
      $('.dropdown.notification_message > .menu').append tag
window.get_notification_messages = get_notification_messages

get_notification_message_content = (uuid) ->
  request = $.ajax
    url: '/get/notification/message/content'
    method: 'POST'
    data: {'uuid': uuid}

  request.done (msg) ->
    msg = JSON.parse msg

    $('.notification_message_content').emtpy()
    $('.notification_message_content').append msg['content']
window.get_notification_message_content = get_notification_message_content

submit_notification_message = (that, message, name, uuid) ->
  $(that).addClass 'disabled'
  $(that).addClass 'loading'

  data = {'message': message, 'name': name}
  if uuid is not null
    data.uuid = uuid

  request = $.ajax
    url: '/submit/notification/message'
    method: 'POST'
    data: data

  request.done (msg) ->
    msg = JSON.parse msg

    if msg['code'] != 'ok'
      $('.alert').html = msg['code']

    $(that).removeClass 'disabled'
    $(that).removeClass 'loading'
window.submit_notification_message = submit_notification_message
