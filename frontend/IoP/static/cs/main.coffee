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

initLineGraph = (graphName) ->
  # ADD LOCAL STORAGE
  sensordata = $.ajax
   url: '/get/plant/sensor/dataset',
   method: 'POST'
   data: {}

  sensordata.done (sensordatamsg) ->
    sensordataset = []
    # console.log sensordatamsg
    for data in JSON.parse(sensordatamsg)
     # console.log data
      sensordataset.push [new Date(data['dt'] * 1000), data['v']]

    smoothPlotter.smoothing = 0.33;
    g = new Dygraph(document.getElementById("graph"),
     sensordataset,
     {
      labels: ['time', graphName],
      plotter: smoothPlotter,
      legend: 'always',
      animatedZooms: true,
      # title: 'dygraphs chart template'
     });
    # window.sensordataset = sensordataset

   return
window.initLineGraph = initLineGraph

initSetTab = (tabName) ->
  $('div.menu.mainMenu').children('.' + tabName).addClass 'active'
  return
window.initSetTab = initSetTab

# sg_nsps == settings get - non specific plant stuff
sg_nsps = () ->
  return


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
      sg_nsps()
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

