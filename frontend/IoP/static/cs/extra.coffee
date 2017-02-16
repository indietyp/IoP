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

get_current_notification_message = (that) ->
  if that != undefined
    $(that).addClass 'disabled'
    $(that).addClass 'loading'

  request = $.ajax
    url: '/get/plant/notification/message'
    method: 'POST'

  request.done (msg) ->
    msg = JSON.parse msg
    $('.notification_message_content').val msg.message
    $('.ui.selection.dropdown').dropdown('set selected', msg.uuid)

    if that != undefined
      $(that).removeClass 'disabled'
      $(that).removeClass 'loading'
  return
window.get_current_notification_message = get_current_notification_message

get_notification_message_content = (uuid) ->
  request = $.ajax
    url: '/get/notification/message/content'
    method: 'POST'
    data: {'uuid': uuid}

  request.done (msg) ->
    msg = JSON.parse msg
    $('.notification_message_content').val msg
window.get_notification_message_content = get_notification_message_content

submit_notification_message = (that, message, name, uuid, responsible=true) ->
  $(that).addClass 'disabled'
  $(that).addClass 'loading'

  data = {'message': message, 'name': name}
  data.responsible = responsible
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
                    <button class="ui button" onclick="delete_general_settings_responsible(\'[[identifier]]\')"><i class="remove icon"></i>
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
                            <input type="text" class="name-[[identifier]]" placeholder="Name" value="[[name]]"><i class="tag icon"></i>
                          </div>
                        </div>
                        <div class="column">
                          <div class="ui fluid left icon input">
                            <input type="text" class="email-[[identifier]]" placeholder="EMail" value="[[email]]"><i class="mail icon"></i>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div class="ui two buttons">
                      <div class="ui basic button fluid green" onclick="change_information_general_settings_responsible(this, \'[[identifier]]\')">Apply</div>
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

change_information_general_settings_responsible = (that, uuid) ->
  $(that).addClass 'disabled'
  $(that).addClass 'loading'

  name = $(".name-#{uuid}").val()
  email = $(".email-#{uuid}").val()

  request = $.ajax
    url: '/change/responsible'
    method: 'POST'
    data:
      uuid: uuid
      name: name
      email: email

  request.done (msg) ->
    msg = JSON.parse msg

    console.log msg
    $(that).removeClass 'disabled'
    $(that).removeClass 'loading'
    get_general_settings_responsibles()
    return

  return
window.change_information_general_settings_responsible = change_information_general_settings_responsible

create_new_general_settings_responsible = () ->
  name = $(".new.name").val()
  email = $(".new.email").val()

  request = $.ajax
    url: '/create/responsible/none'
    method: 'POST'
    data:
      name: name
      email: email
      wizard: 'no'

  request.done (msg) ->
    msg = JSON.parse msg

    console.log msg
    $(".new.name").val('')
    $(".new.email").val('')
    get_general_settings_responsibles()

  return
window.create_new_general_settings_responsible = create_new_general_settings_responsible

modify_plant_durations = (that) ->
  $(that).addClass 'disabled'
  $(that).addClass 'loading'

  request = $.ajax
    url: '/change/plant/intervals'
    method: 'POST'
    data:
      notification: $("#flat-slider-general-interval").slider("option", "value");
      connection: $("#flat-slider-dead-interval").slider("option", "value");
      non_persistant: $("#flat-slider-non-persistant-interval").slider("option", "value");

  request.done (msg) ->
    msg = JSON.parse msg
    $(that).removeClass 'disabled'
    $(that).removeClass 'loading'
  return
window.modify_plant_durations = modify_plant_durations

get_day_night = () ->
  request = $.ajax
    url: '/get/day_night'
    method: 'POST'

  request.done (msg) ->
    msg = JSON.parse msg

    if msg.ledbar
      $('.field.ledbar > .ui.checkbox > input').prop 'checked', true
    if msg.display
      $('.field.display > .ui.checkbox > input').prop 'checked', true
    if msg.generalleds
      $('.field.generalleds > .ui.checkbox > input').prop 'checked', true
    if msg.notification
      $('.field.notification > .ui.checkbox > input').prop 'checked', true

    start = msg.start.toString()

    if start.length == 3
      start = start.slice 0, 1
    else
      start = start.slice 0, 2

    stop = msg.stop.toString()

    if stop.length == 3
      stop = stop.slice 0, 1
    else
      stop = stop.slice 0, 2

    $("#flat-slider-time-interval")
        .slider({
            max: 24,
            min: 0,
            range: true,
            values: [parseInt(start), parseInt(stop)]
        })
        .slider("pips", {
            first: "pip",
            last: "pip"
        })
  return
window.get_day_night = get_day_night

modify_day_night = (that) ->
  $(that).addClass 'disabled'
  $(that).addClass 'loading'
  time = $("#flat-slider-time-interval").slider "option", "values"

  request = $.ajax
    url: '/change/day_night'
    method: 'POST'
    data:
      stop: parseInt(time[1].toString() + '00')
      start: parseInt(time[0].toString() + '00')
      ledbar: $('.field.ledbar > .ui.checkbox > input').prop 'checked'
      display: $('.field.display > .ui.checkbox > input').prop 'checked'
      generalleds: $('.field.generalleds > .ui.checkbox > input').prop 'checked'
      notification: $('.field.notification > .ui.checkbox > input').prop 'checked'

  request.done (msg) ->
    msg = JSON.parse msg
    $(that).removeClass 'disabled'
    $(that).removeClass 'loading'
  return
window.modify_day_night = modify_day_night

init_manage = () ->
  request = $.ajax
    url: '/get/manage'
    method: 'POST'

  request.done (msg) ->
    msg = JSON.parse msg

    html = ""
    main = "
    <div class='item'>
      <div class='ui equal width grid'>
        <div class='column'>
          <a class='ui [[COLOR]] ribbon label' [[ADDITIONAL]]>[[MASTER]]</a>
          <span style='font-weight:bold'>[[NAME]]</span>
        </div>
        [[SLAVE]]
        <div class='column right aligned'>
          <div class='ui icon buttons'>
            <button class='ui button'>
              <i class='edit icon' />
            </button>
            <button class='ui button'>
              <i class='checkmark icon' />
            </button>
            <button class='ui button'>
              <i class='erase icon' />
            </button>
          </div>
        </div>
      </div>
    </div>"
    slave = "
    <div class='column'>
      My master is
      <div class='ui inline dropdown [[NAME]] slave'>
        <div class='text'>[[HOST]]</div>
        <i class='dropdown icon' />
        <div class='menu'>
          [[MASTERS]]
        </div>
      </div>
    </div>
    <script>
      $('.[[NAME]].slave').dropdown({});
    </script>"

    masters = {}
    slaves = {}

    for plant in msg
      if plant.role == 'master'
        masters[plant.uuid] = plant
        # role = 'Master'
      else
        slaves[plant.uuid] = plant
        # role = 'Slave'

    for k, plant of masters
      html += main.replace('[[MASTER]]', 'Master').replace('[[NAME]]', plant.name).replace('[[SLAVE]]', '').replace('[[COLOR]]', 'red').replace('[[ADDITIONAL]]', '')

    for k, plant of slaves
      content = main.replace('[[MASTER]]', 'Slave').replace(/\[\[NAME\]\]/, plant.name).replace('[[COLOR]]', 'orange').replace('[[ADDITIONAL]]', style='padding-right:2em')
      processed_slave = slave.replace('[[NAME]]', plant.name).replace('[[HOST]]', masters[plant.role].name)
      processed_masters = ''

      for k, master of masters
        processed_masters += "<div class='item' data-value='#{master.uuid}'>#{master.name}</div>"

      processed_slave = processed_slave.replace('[[MASTERS]]', processed_masters)
      html += content.replace('[[SLAVE]]', processed_slave)

    $('.ui.relaxed.divided.list').html html

  return
window.init_manage = init_manage
