getCurrentPlant = () ->
  request = $.ajax
    url: '/get/current/plant',
    method: 'POST',
    # not as good as you might think!
    # pls find other solution, thank you!
    async: false
    data: {}

  request.done (msg) ->
    return

  request.fail (jqXHR, textStatus) ->
    $('section.mainContent').html('Request failed:' + textStatus)
    return
  return request.responseText

getCurrentPUUID = () ->
  request = $.ajax
    url: '/get/current/p_uuid',
    method: 'POST',
    # not as good as you might think!
    # pls find other solution, thank you!
    async: false
    data: {}

  request.done (msg) ->
    return

  request.fail (jqXHR, textStatus) ->
    $('section.mainContent').html('Request failed:' + textStatus)
    return
  return request.responseText

getCurrentSensor = () ->
  request = $.ajax
    url: '/get/current/sensor',
    method: 'POST',
    async: false
    data: {}

  request.done (msg) ->
    return

  request.fail (jqXHR, textStatus) ->
    $('section.mainContent').html('Request failed:' + textStatus)
    return
  return request.responseText

setuppredicted = (db, jsonmsg, plant, sensor, graphName) ->
  bulkadd = []
  display = []
  # console.log display
  for entry in jsonmsg['predicted']
    bulkadd.push {plant: plant, sensor: sensor, value: entry['value'], timestamp: entry['timestamp']}

  db.predicted.bulkAdd(bulkadd).then (result) ->
    db.real.where('[plant+sensor]').equals([plant, sensor]).sortBy('timestamp').then (array) ->
      for result in array
        display.push [new Date(result.timestamp * 1000), result.value, null]
      db.predicted.where('[plant+sensor]').equals([plant, sensor]).each (result) ->
        display.push [new Date(result.timestamp * 1000), null, result.value]
        return
      .then (result) ->
        smoothPlotter.smoothing = 0.33
        g = new Dygraph(document.getElementById("graph"),
          display,
          {
            labels: ['time', graphName, 'prediction'],
            plotter: smoothPlotter,
            legend: 'always',
            animatedZooms: true,
          })
        return
      .catch (error) ->
        console.log error
        return
    .catch (error) ->
      console.log error
      return
    return
  .catch (error) ->
    console.log error
    return
  return


initLineGraph = (graphName) ->
  sensor = getCurrentSensor()
  plant = getCurrentPUUID()
  db = new Dexie 'sensordata'

  db.version(1).stores({
    real: '++id, sensor, plant, timestamp, [plant+sensor]',
    predicted: '++id, sensor, plant, [plant+sensor]'
  })
  db.open().catch ->
    alert('Uh oh : ' + error)

  collection_count = -1
  db.real.where('[plant+sensor]').equals([plant, sensor]).count().then (result) ->
    display = []
    console.log result
    if result == 0
      display = []
      console.log 'building indexedDB [partial]'
      count = $.ajax
        url: '/get/plant/sensor/data/count'
        method: 'POST'
        data: {'sensor': sensor}

      count.done (msg) ->
        count = JSON.parse(msg)['count']
        i = 0
        start = 0
        stop = 0

        while stop < count
          i+=1
          start = if i == 1 then 0 else stop
          # stop = Math.floor(Math.pow(i, 3))
          stop = Math.floor(Math.pow(i, 2.8))
          console.log stop - start
          if i == 1
            smoothPlotter.smoothing = 0.33
            g = new Dygraph(document.getElementById("graph"),
              display,
              {
                labels: ['time', graphName, 'prediction'],
                plotter: smoothPlotter,
                legend: 'always',
                animatedZooms: true,
              })

          sensordata = $.ajax
            url: '/get/plant/sensor/data/range'
            method: 'POST'
            data: {'sensor': sensor, 'start': start, 'stop': stop}

          sensordata.done (sensordatamsg) ->
            bulkadd = []
            json_msg = JSON.parse(sensordatamsg)
            for data in json_msg
              display.unshift [new Date(data['timestamp'] * 1000), data['value'], null]
              bulkadd.push {plant: plant, sensor: sensor, value: data['value'], timestamp: data['timestamp']}

            display.sort (a, b) ->
              return a[0] - b[0];

            db.real.bulkAdd(bulkadd).then (result) ->
              g.updateOptions( { 'file': display } )
              return
            .catch (error) ->
              console.log error
              return
            return

        prediction = $.ajax
          url: '/get/plant/sensor/prediction'
          method: 'POST'
          data: {'sensor': sensor}

        prediction.done (prediction) ->
          json_prediction = JSON.parse(prediction)
          bulkadd = []
          console.log 'predicting'

          for data in json_prediction
            display.push [new Date(data['timestamp'] * 1000), null, data['value']]
            bulkadd.push {plant: plant, sensor: sensor, value: data['value'], timestamp: data['timestamp']}

          db.predicted.bulkAdd(bulkadd).then (result) ->
            g.updateOptions({'file': display})
            return
        return


      # sensordata = $.ajax
      #   url: '/get/plant/sensor/dataset',
      #   method: 'POST'
      #   data: {}

      # sensordata.done (sensordatamsg) ->
        # bulkadd = []
        # json_msg = JSON.parse(sensordatamsg)
        # for data in json_msg['real']
        #   display.push [new Date(data['timestamp'] * 1000), data['value'], null]
        #   bulkadd.push {plant: plant, sensor: sensor, value: data['value'], timestamp: data['timestamp']}

        # db.real.bulkAdd(bulkadd).then (result) ->
        #   bulkadd = []
        #   for data in json_msg['predicted']
        #     display.push [new Date(data['timestamp'] * 1000), null, data['value']]
        #     bulkadd.push {plant: plant, sensor: sensor, value: data['value'], timestamp: data['timestamp']}

        #   db.predicted.bulkAdd(bulkadd).then (result) ->
        #     smoothPlotter.smoothing = 0.33;
        #     g = new Dygraph(document.getElementById("graph"),
        #       display,
        #       {
        #         labels: ['time', graphName, 'prediction'],
        #         plotter: smoothPlotter,
        #         legend: 'always',
        #         animatedZooms: true,
        #       });
        #     return
        #   .catch (error) ->
        #     console.log error
        #     return
        #   return
        # .catch (error) ->
        #   console.log error
        #   return
        return
      return
    else
      console.log 'using indexedDB'
      db.real.where('[plant+sensor]').equals([plant, sensor]).reverse().sortBy('timestamp').then (result) ->
        result = result[0]
        latestdata = $.ajax
          url: '/get/plant/sensor/dataset/custom'
          method: 'POST'
          data: {'latest_timestamp': result['timestamp']}

        latestdata.done (msg) ->
          display = []
          jsonmsg = JSON.parse msg
          console.log jsonmsg['real'].length

          bulkadd = []
          for entry in jsonmsg['real']
            bulkadd.push {plant: plant, sensor: sensor, value: entry['value'], timestamp: entry['timestamp']}

          db.real.bulkAdd(bulkadd).then (result) ->
            bulkadd = []
            console.log jsonmsg['predicted'].length
            if jsonmsg['predicted'].length > 0
              db.predicted.clear().then (result) ->
                console.log 'terminating predicted table'
                setuppredicted(db, jsonmsg, plant, sensor, graphName)
            else
              console.log 'continuing'
              setuppredicted(db, jsonmsg, plant, sensor, graphName)
            return

          .catch (error) ->
            console.log error
            return
        return
      .catch (error) ->
        console.log error
        return
    return
  .catch (error) ->
    console.log error
    return

  return
window.initLineGraph = initLineGraph

initSetTab = (tabName) ->
  $('div.menu.mainMenu').children('.' + tabName).addClass 'active'
  return
window.initSetTab = initSetTab

# sg_nsps == settings get - non specific plant stuff
sg_nsps = () ->
  request = $.ajax
    url: '/get/plant/settings/data/non_specific',
    method: 'POST'
    data: {}

  request.done (msg) ->
    msg = JSON.parse msg
    $('#__nsps_name input').val msg['name']
    $('#__nsps_type input').val msg['type']
    $('#__nsps_location input').val msg['location']

    $('#__nsps_segment').fadeIn 'slow'
    return
  return
window.sg_nsps = sg_nsps

sg_nsps_reset = (that) ->
  $(that).addClass 'disabled'
  $(that).addClass 'loading'
  sg_nsps()
  $( document ).ajaxComplete () ->
    $(that).removeClass 'disabled'
    $(that).removeClass 'loading'
  return
window.sg_nsps_reset = sg_nsps_reset

sg_nsps_submit = (that) ->
  $(that).addClass 'disabled'
  $(that).addClass 'loading'

  request = $.ajax
    url: '/update/plant/settings/non_specific',
    method: 'POST'
    data: {'name': $('#__nsps_name input').val(), 'location': $('#__nsps_location input').val(), 'type': $('#__nsps_type input').val()}

  request.done (msg) ->
    msg = JSON.parse msg
    $(that).removeClass 'disabled'
    $(that).removeClass 'loading'

    if msg['info'] == 'change'
      window.location = '/plant/' + msg['plant'] + '/overview'

window.sg_nsps_submit = sg_nsps_submit

# sg_ssps == settings get - sensor specific plant stuff
sg_ssps = () ->
  request = $.ajax
    url: '/get/plant/settings/data/sensor_ranges',
    method: 'POST'
    data: {}

  request.done (msg) ->
    msg = JSON.parse msg

    for item in msg
      settings = item['settings']
      range_request = $.ajax
        url: '/get/sensor/range',
        method: 'POST'
        data: {'sensor': item['sensor']}
        async: false

      range_request.done (range) ->
        data = JSON.parse(range)
        range = data['range']
        sensor = data['sensor']
        current_settings = []
        current_settings.push settings['yellow']['min']
        current_settings.push settings['green']['min']
        current_settings.push settings['green']['max']
        current_settings.push settings['yellow']['max']

        $("#flat-slider-vertical-" + sensor)
          .slider({
            max: range['max'],
            min: range['min'],
            values: current_settings,
            orientation: "vertical"
          })
          .slider("pips", {
            first: "pip",
            last: "pip"
          })
          .slider("float")
    $('.__ssps_segment').fadeIn 'slow'
    return
  return
window.sg_ssps = sg_ssps

sg_ssps_submit = (that) ->
  $(that).addClass 'disabled'
  $(that).addClass 'loading'

  name = $(that).parent().parent().parent().attr('class').split(' ')['2'].split('_')[1]
  values = $("#flat-slider-vertical-" + name).slider( "values" )
  values = values.sort (a, b) -> return a - b
  # console.log values
  $("#flat-slider-vertical-" + name).slider( "values", values )

  request = $.ajax
    url: '/update/plant/ranges',
    method: 'POST'
    data: {'new': values, 'sensor': name}

  request.done (msg) ->
    # delay 100
    $(that).removeClass 'disabled'
    $(that).removeClass 'loading'
  return
window.sg_ssps_submit = sg_ssps_submit

sg_ssps_reset = (that) ->
  $(that).addClass 'disabled'
  $(that).addClass 'loading'
  name = $(that).parent().parent().parent().attr('class').split(' ')['2'].split('_')[1]
  request = $.ajax
    url: '/get/plant/sensor/ranges'
    method: 'POST'
    data: {'sensor': name}

  request.done (msg) ->
    msg = JSON.parse msg
    values = []
    values.push msg['yellow']['min']
    values.push msg['green']['min']
    values.push msg['green']['max']
    values.push msg['yellow']['max']
    $("#flat-slider-vertical-" + name).slider( "values", values )
    $(that).removeClass 'disabled'
    $(that).removeClass 'loading'
    return
  return
window.sg_ssps_reset = sg_ssps_reset

# settings get - responsible specific plant stuff
sg_rsps = () ->
  request = $.ajax
    url: '/get/responsibles',
    method: 'POST'
    data: {}

  request.done (msg) ->
    msg = JSON.parse msg

    for person in msg
      $('#select').append('<option value="' + person['email'] + '">' + person['name'] + '</option>')

    current = $.ajax
      url: '/get/plant/responsible',
      method: 'POST'
      data: {}

    current.done (msg) ->
      msg = JSON.parse(msg)
      $('#select').dropdown('set selected', msg['email'])
      $('#__rsps_input').val(msg['email'])
      $('#__rsps_segment').fadeIn 'slow'
      return
  return
window.sg_rsps = sg_rsps

sg_rsps_change = (that) ->
  $('#__rsps_input').val($(that).val())
  return
window.sg_rsps_change = sg_rsps_change

# SUMBIT VAL + NAME AND COMPARE
sg_rsps_submit = (that) ->
  $(that).addClass 'disabled'
  $(that).addClass 'loading'
  name = $("#select option:selected").text()
  email = $('#__rsps_input').val()

  request = $.ajax
    url: '/update/plant/responsible',
    method: 'POST'
    data: {'name': name, 'email': email}

  request.done (msg) ->
    $(that).removeClass 'disabled'
    $(that).removeClass 'loading'
    return
  return
window.sg_rsps_submit = sg_rsps_submit

# SUMBIT VAL + NAME AND COMPARE
sg_rsps_create = (that) ->
  $(that).addClass 'disabled'
  $(that).addClass 'loading'
  wizard = $("#create_select option:selected").text()
  console.log wizard
  name = $('#__rspsc_name').val()
  email = $('#__rspsc_email').val()

  request = $.ajax
    url: '/create/responsible',
    method: 'POST'
    data: {'name': name, 'email': email, 'wizard': wizard}

  request.done (msg) ->
    $(that).removeClass 'disabled'
    $(that).removeClass 'loading'
    return
  return
window.sg_rsps_create = sg_rsps_create

sg_rsps_reset = (that) ->
  $(that).addClass 'disabled'
  $(that).addClass 'loading'
  current = $.ajax
    url: '/get/plant/responsible',
    method: 'POST'
    data: {}

  current.done (msg) ->
    msg = JSON.parse(msg)
    $('#select').dropdown('set selected', msg['email'])
    $('#__rsps_input').val(msg['email'])
    $(that).removeClass 'disabled'
    $(that).removeClass 'loading'
    return
window.sg_rsps_reset = sg_rsps_reset

device_discover = () ->
  $('div.ui.selection.dropdown.discover > div.default.text').html 'please wait a couple of seconds'
  current = $.ajax
    url: '/get/discover'
    method: 'POST'
    data: {}

  current.done (msg) ->
    msg = JSON.parse msg
    $('div.ui.selection.dropdown.discover > div.menu').empty()

    for item in msg
      if msg['master'] == true
        msg['role'] = 'master'
      else
        msg['role'] = 'slave'
      $('div.ui.selection.dropdown.discover > div.menu').append '<div class="item ' + msg['role'] + '" data-value="' + msg['ip'] + '"> ' + msg['ip'] + ' </div>'
      # return
    $('div.ui.selection.dropdown.discover > div.default.text').html 'IP-Adress - done loading'
    # return
  return

window.device_discover = device_discover

device_discover = () ->
  $('div.ui.selection.dropdown.master > div.default.text').html 'please wait a couple of seconds'
  current = $.ajax
    url: '/get/master'
    method: 'POST'
    data: {}

  current.done (msg) ->
    msg = JSON.parse msg
    $('div.ui.selection.dropdown.master > div.menu').empty()

    for item in msg
      content = "#{msg['name']} <#{msg['ip']}>"
      $('div.ui.selection.dropdown.master > div.menu').append "<div class='item' data-value='#{msg['uuid']}'>#{content}</div>"
    $('div.ui.selection.dropdown.master > div.default.text').html 'ready for selection'
    return
  return

window.device_discover = device_discover

add_plant_responsibles = () ->
  $('div.ui.selection.dropdown.responsible > div.default.text').html 'please wait a couple of seconds'
  current = $.ajax
    url: '/get/responsibles',
    method: 'POST'
    data: {}

  current.done (msg) ->
    msg = JSON.parse msg

    $('div.ui.selection.dropdown.responsible > div.menu').empty()
    for person in msg
      $('div.ui.selection.dropdown.responsible > div.menu').append '<div class="item" data-value="' + person['email'] + '">' + person['name'] + ' &lt' + person['email'] + '&gt </div>'

    $('div.ui.selection.dropdown.responsible > div.default.text').html 'Responsible - done loading'

  return

window.add_plant_responsibles = add_plant_responsibles

register_new_plant = () ->
  console.log('HEY')
  a = $('input.name').val()
  b = $('input.location').val()
  c = $('input.species').val()
  d = $('input.notification_interval').val()
  e = $('.ui.selection.dropdown.responsible .active.selected').data()['value']
  f = $('.ui.selection.dropdown.discover .active.selected').data()['value']
  current = $.ajax
    url: '/create/plant'
    method: 'POST'
    data: {'name': a, 'location': b, 'species': c, 'interval': d, 'email': e, 'ip': f}

  current.done (msg) ->
    window.location.href = '/'
  return

window.register_new_plant = register_new_plant

$ ->
  $('a.item.add_plant').click (e) ->
    request = $.ajax
      url: '/display/add_plant/',
      method: 'POST'
      data: {}

    request.done (msg) ->
      $('section.mainContent').fadeOut 'slow', () ->
        $('section.mainContent').html(msg)
        $('section.mainContent').html(msg).fadeIn('slow')
        return
      window.history.pushState({}, '', '/add_plant')

    return

  $('div.menu.mainMenu a').click (e) ->
    $(this).parent().children('.active').removeClass 'active'
    $(this).addClass 'active'
    return

  $('a.item.global_settings').click (e) ->
    request = $.ajax
      url: '/get/general/settings',
      method: 'POST'
      data: {}

    request.done (msg) ->
      $('section.mainContent').html(msg)
      window.history.pushState({}, '', '/global/settings')
      $('div.menu.mainMenu a').parent().children('.active').removeClass 'active'
      # $('div.menu.mainMenu a.overview').addClass 'active'
      $('div.pusher div.ui.segment div.information h1.ui.header.plant_header').html _.capitalize('Global Settings')
      $('div.iopheader div.ui.menu.secondary').css('display', 'none')
      return

    request.fail (jqXHR, textStatus) ->
      $('section.mainContent').html('Request failed:' + textStatus)
      return

    window.history.pushState({}, '', '/global/settings')
    return

  $('a.item.plant_settings').click (e) ->
    request = $.ajax
      url: '/get/plant/settings',
      method: 'POST'
      data: {}

    request.done (msg) ->
      $('section.mainContent').html(msg)
      $('div.menu.mainMenu a').parent().children('.active').removeClass 'active'

      # sg_nsps == settings get - non specific plant stuff
      # sg_nsps()
      return

    request.fail (jqXHR, textStatus) ->
      $('section.mainContent').html('Request failed:' + textStatus)
      return

    window.history.pushState({}, '', '/plant/' +  getCurrentPlant()  + '/settings')
    return

  $('a.item.plant').click (e) ->
    plant =  $(this).attr('class').split(' ')[2]

    request = $.ajax
      url: '/get/plant/overview',
      method: 'POST'
      data: {plant: plant}

    request.done (msg) ->
      $('section.mainContent').fadeOut 'slow', () ->
        $('section.mainContent').html(msg).fadeIn('slow')
        return
      window.history.pushState({}, '', '/plant/' + plant + '/overview')
      $('div.menu.mainMenu a').parent().children('.active').removeClass 'active'
      $('div.menu.mainMenu a.overview').addClass 'active'
      $('div.pusher div.ui.segment div.information h1.ui.header.plant_header').html _.capitalize(plant)
      $('div.iopheader div.ui.menu.secondary').css('display', 'inherit')
      return

    request.fail (jqXHR, textStatus) ->
      $('section.mainContent').html('Request failed:' + textStatus)
      return
    return

  $('a.item.sensor').click (e) ->
    sensor =  $(this).attr('class').split(' ')[2]

    request = $.ajax
      url: '/get/plant/sensor',
      method: 'POST'
      data: {sensor: sensor}

    request.done (msg) ->
      $('section.mainContent').html(msg)
      return

    request.fail (jqXHR, textStatus) ->
      $('section.mainContent').html('Request failed:' + textStatus)
      return

    window.history.pushState({}, '', '/plant/' +  getCurrentPlant()  + '/' + sensor)
    return

  $('a.item.overview').click (e) ->
    request = $.ajax
      url: '/get/plant/overview',
      method: 'POST'
      data: {}

    request.done (msg) ->
      $('section.mainContent').html(msg)
      window.history.pushState({}, '', '/plant/' + getCurrentPlant() + '/overview')
      return

    request.fail (jqXHR, textStatus) ->
      $('section.mainContent').html('Request failed:' + textStatus)
      return
    return
  return
