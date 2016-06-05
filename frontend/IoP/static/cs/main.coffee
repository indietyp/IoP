getOverview = () ->
  request = $.ajax
    url: '/get/plant/overview',
    method: 'POST'
    data: {}

  request.done (msg) ->
    $('section.mainContent').html(msg);
    window.history.pushState({}, '', '/plant/marta/overview');
    return

  request.fail (jqXHR, textStatus) ->
    $('section.mainContent').html('Request failed:' + textStatus);
    return
  return
window.getOverview = getOverview

getSensor = (sensor) ->
  request = $.ajax
    url: '/get/plant/sensor',
    method: 'POST'
    data: {sensor: sensor}

  request.done (msg) ->
    $('section.mainContent').html(msg);
    return

  request.fail (jqXHR, textStatus) ->
    $('section.mainContent').html('Request failed:' + textStatus);
    return

  window.history.pushState({}, '', '/plant/marta/' + sensor);
  return
window.getSensor = getSensor

goToPlant = (plant) ->
  request = $.ajax
    url: '/get/plant/overview',
    method: 'POST'
    data: {plant: plant}

  request.done (msg) ->
    $('section.mainContent').html(msg);
    window.history.pushState({}, '', '/plant/' + plant + '/overview');
    return

  request.fail (jqXHR, textStatus) ->
    $('section.mainContent').html('Request failed:' + textStatus);
    return
  return

initSetTab = (tabName) ->
  $('div.menu.mainMenu').children('.' + tabName).addClass 'active'
  return
window.initSetTab = initSetTab

$ ->
  $('div.menu.mainMenu a').click (e) ->
    $(this).parent().children('.active').removeClass 'active'
    $(this).addClass 'active'
    return
  return
