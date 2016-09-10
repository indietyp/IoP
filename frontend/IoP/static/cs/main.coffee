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
    $('section.mainContent').html('Request failed:' + textStatus);
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
    $('section.mainContent').html('Request failed:' + textStatus);
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
    $('section.mainContent').html('Request failed:' + textStatus);
    return
  return request.responseText

initLineGraph = (graphName) ->
  sensor = getCurrentSensor()
  plant = getCurrentPUUID()
  current = localStorage.getItem(sensor + ',' + plant)

  if current is null or current == ''
    console.log 'building localStorage'
    sensordata = $.ajax
      url: '/get/plant/sensor/dataset',
      method: 'POST'
      data: {}

    sensordata.done (sensordatamsg) ->
      sensordataset = []

      for data in JSON.parse(sensordatamsg)['real']
        sensordataset.push [new Date(data['timestamp'] * 1000), data['value'], null]

      for data in JSON.parse(sensordatamsg)['predicted']
        sensordataset.push [new Date(data['timestamp'] * 1000), null, data['value']]

      localStorage.setItem(sensor + ',' + plant, sensordatamsg)

      smoothPlotter.smoothing = 0.33;
      g = new Dygraph(document.getElementById("graph"),
       sensordataset,
       {
        labels: ['time', graphName, 'prediction'],
        plotter: smoothPlotter,
        legend: 'always',
        animatedZooms: true,
       });
      return
    return
  else
    console.log 'using localStorage'
    current_data = JSON.parse(current)
    sensordata = $.ajax
      url: '/get/plant/sensor/dataset/custom',
      method: 'POST'
      data: {'latest_timestamp': current_data['real'][current_data['real'].length - 1]['timestamp']}

    sensordata.done (sensordatamsg) ->
      sensordataset = []

      for data in JSON.parse(sensordatamsg)['real']
        current_data.push data

      current_data['predicted'] = JSON.parse(sensordatamsg)['predicted']
      localStorage.setItem(sensor + ',' + plant, JSON.stringify(current_data))

      for data in current_data['real']
        sensordataset.push [new Date(data['timestamp'] * 1000), data['value'], null]

      for data in current_data['predicted']
        sensordataset.push [new Date(data['timestamp'] * 1000), null, data['value']]

      smoothPlotter.smoothing = 0.33;
      g = new Dygraph(document.getElementById("graph"),
       sensordataset,
       {
        labels: ['time', graphName, 'prediction'],
        plotter: smoothPlotter,
        legend: 'always',
        animatedZooms: true,
       });
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

    $('#__nsps_segment').fadeIn 'slow';
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
            .slider("float");
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
  $("#flat-slider-vertical-" + name).slider( "values", values );

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
    $("#flat-slider-vertical-" + name).slider( "values", values );
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
      $('#select').dropdown('set selected', msg['email']);
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
  name = $("#select option:selected").text();
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
  wizard = $("#create_select option:selected").text();
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
    $('#select').dropdown('set selected', msg['email']);
    $('#__rsps_input').val(msg['email'])
    $(that).removeClass 'disabled'
    $(that).removeClass 'loading'
    return
window.sg_rsps_reset = sg_rsps_reset

$ ->
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
      $('section.mainContent').html(msg);
      window.history.pushState({}, '', '/global/settings');
      $('div.menu.mainMenu a').parent().children('.active').removeClass 'active'
      # $('div.menu.mainMenu a.overview').addClass 'active'
      $('div.pusher div.ui.segment div.information h1.ui.header.plant_header').html _.capitalize('Global Settings')
      $('div.iopheader div.ui.menu.secondary').css('display', 'none')
      return

    request.fail (jqXHR, textStatus) ->
      $('section.mainContent').html('Request failed:' + textStatus);
      return

    window.history.pushState({}, '', '/global/settings');
    return

  $('a.item.plant_settings').click (e) ->
    request = $.ajax
      url: '/get/plant/settings',
      method: 'POST'
      data: {}

    request.done (msg) ->
      $('section.mainContent').html(msg);
      $('div.menu.mainMenu a').parent().children('.active').removeClass 'active'

      # sg_nsps == settings get - non specific plant stuff
      # sg_nsps()
      return

    request.fail (jqXHR, textStatus) ->
      $('section.mainContent').html('Request failed:' + textStatus);
      return

    window.history.pushState({}, '', '/plant/' +  getCurrentPlant()  + '/settings');
    return

  $('a.item.plant').click (e) ->
    plant =  $(this).attr('class').split(' ')[2]

    request = $.ajax
      url: '/get/plant/overview',
      method: 'POST'
      data: {plant: plant}

    request.done (msg) ->
      $('section.mainContent').fadeOut 'slow', () ->
        $('section.mainContent').html(msg).fadeIn('slow');
        return
      window.history.pushState({}, '', '/plant/' + plant + '/overview');
      $('div.menu.mainMenu a').parent().children('.active').removeClass 'active'
      $('div.menu.mainMenu a.overview').addClass 'active'
      $('div.pusher div.ui.segment div.information h1.ui.header.plant_header').html _.capitalize(plant)
      $('div.iopheader div.ui.menu.secondary').css('display', 'inherit')
      return

    request.fail (jqXHR, textStatus) ->
      $('section.mainContent').html('Request failed:' + textStatus);
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
      $('section.mainContent').html('Request failed:' + textStatus);
      return

    window.history.pushState({}, '', '/plant/' +  getCurrentPlant()  + '/' + sensor);
    return

  $('a.item.overview').click (e) ->
    request = $.ajax
      url: '/get/plant/overview',
      method: 'POST'
      data: {}

    request.done (msg) ->
      $('section.mainContent').html(msg);
      window.history.pushState({}, '', '/plant/' + getCurrentPlant() + '/overview');
      return

    request.fail (jqXHR, textStatus) ->
      $('section.mainContent').html('Request failed:' + textStatus);
      return
    return
  return
