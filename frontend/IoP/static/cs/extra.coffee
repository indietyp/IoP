get_notification_messages = (callback) ->
  console.log 'TEST!'
  request = $.ajax
    url: '/get/notification/message/names'
    method: 'POST'
    data: {}

  request.done (msg) ->
    msg = JSON.parse msg
    console.log msg
    $('.dropdown.notification_message > .menu').emtpy
    for message in msg

      uuid = message['uuid']
      name = message['name']

      tag = "<div class='item' data-value='#{uuid}'>#{name}</div>"
      console.log tag
      $('.dropdown.notification_message > .menu').append tag
    callback('finished' )
window.get_notification_messages = get_notification_messages

get_notification_message_content = (uuid) ->
  request = $.ajax
    url: '/get/notification/message/content'
    method: 'POST'
    data: {'uuid': uuid}

  request.done (msg) ->
    msg = JSON.parse msg
    $('.notification_message_content').html msg
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


get_general_settings_responsibles = () ->
  request = $.ajax
    url: '/get/responsibles'
    method: 'POST'

  request.done (msg) ->
    msg = JSON.parse msg

    $(".ui.middle.aligned.divided.list").html ''
    for person in msg
      tab =   '<div class="item">
                <div class="right floated content">
                  <div class="ui small basic icon buttons">
                    <button class="ui button">
                      <div class="ui radio checkbox">
                        <input type="radio" name="wizard" [[checked]] onChange="change_wizard_general_settings_responsible(this, \'[[identifier]]\')">
                        <label><i class="wizard icon"></i>
                        </label>
                      </div>
                    </button>
                    <button onclick="$(\'.[[identifier]]\').accordion(\'toggle\', 0);" class="ui button"><i class="edit icon"></i>
                    </button>
                    <button class="ui button"><i class="remove icon"></i>
                    </button>
                  </div>
                </div><img src="https://source.unsplash.com/category/nature" class="ui avatar image">
                <div class="content">[[name]]</div>
                <div class="ui accordion [[identifier]]">
                  <div style="height:0;padding:0" class="title"></div>
                  <div style="margin-top:1%" class="content">
                    <div class="ui grid">
                      <div class="two column row relaxed">
                        <div style="margin-bottom:1%" class="column">
                          <div class="ui fluid left icon input">
                            <input type="text" placeholder="Name" value="[[name]]"><i class="tag icon"></i>
                          </div>
                        </div>
                        <div class="column">
                          <div class="ui fluid left icon input">
                            <input type="text" placeholder="EMail" value="[[email]]"><i class="home icon"></i>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div class="ui two buttons">
                      <div class="ui basic button fluid green" onclick="submit_responsible_changes([[identifier]])">Apply</div>
                      <div class="ui basic button fluid red">Reset</div>
                    </div>
                  </div>
                </div>
                <script type="text/javascript">
                </script>
              </div>'
      tab = tab.replace /\[\[identifier\]\]/g, person.uuid
      tab = tab.replace /\[\[name\]\]/g, person.name
      tab = tab.replace /\[\[email\]\]/g, person.email

      if person.wizard == false
        replace = ''
      else
        replace = 'checked'

      tab = tab.replace /\[\[checked\]\]/g, replace
      $(".ui.middle.aligned.divided.list").append tab
window.get_general_settings_responsibles = get_general_settings_responsibles

delete_general_settings_responsible = (uuid) ->
  request = $.ajax
    url: '/remove/responsible'
    method: 'POST'
    data:
      uuid: uuid

  request.done (msg) ->
    msg = JSON.parse msg

    console.log msg
    get_general_settings_responsibles()
    return
  return

window.delete_general_settings_responsible = delete_general_settings_responsible

change_wizard_general_settings_responsible = (that, uuid) ->
  if that.checked
    request = $.ajax
      url: '/change/responsible/wizard'
      method: 'POST'
      data:
        uuid: uuid

    request.done (msg) ->
      msg = JSON.parse msg

      console.log msg
      get_general_settings_responsibles()
      return

  return
window.change_wizard_general_settings_responsible = change_wizard_general_settings_responsible
