// Generated by CoffeeScript 1.12.2
(function() {
  var add_plant_responsibles, device_discover, device_master, getCurrentPUUID, getCurrentPlant, getCurrentSensor, initLineGraph, initSetTab, register_new_plant, setuppredicted, sg_nsps, sg_nsps_reset, sg_nsps_submit, sg_rsps, sg_rsps_change, sg_rsps_create, sg_rsps_reset, sg_rsps_submit, sg_ssps, sg_ssps_reset, sg_ssps_submit;

  getCurrentPlant = function() {
    var request;
    request = $.ajax({
      url: '/get/current/plant',
      method: 'POST',
      async: false,
      data: {}
    });
    request.done(function(msg) {});
    request.fail(function(jqXHR, textStatus) {
      $('section.mainContent').html('Request failed:' + textStatus);
    });
    return request.responseText;
  };

  getCurrentPUUID = function() {
    var request;
    request = $.ajax({
      url: '/get/current/p_uuid',
      method: 'POST',
      async: false,
      data: {}
    });
    request.done(function(msg) {});
    request.fail(function(jqXHR, textStatus) {
      $('section.mainContent').html('Request failed:' + textStatus);
    });
    return request.responseText;
  };

  getCurrentSensor = function() {
    var request;
    request = $.ajax({
      url: '/get/current/sensor',
      method: 'POST',
      async: false,
      data: {}
    });
    request.done(function(msg) {});
    request.fail(function(jqXHR, textStatus) {
      $('section.mainContent').html('Request failed:' + textStatus);
    });
    return request.responseText;
  };

  setuppredicted = function(db, jsonmsg, plant, sensor, graphName) {
    var bulkadd, display, entry, j, len, ref;
    bulkadd = [];
    display = [];
    ref = jsonmsg['predicted'];
    for (j = 0, len = ref.length; j < len; j++) {
      entry = ref[j];
      bulkadd.push({
        plant: plant,
        sensor: sensor,
        value: entry['value'],
        timestamp: entry['timestamp']
      });
    }
    db.predicted.bulkAdd(bulkadd).then(function(result) {
      db.real.where('[plant+sensor]').equals([plant, sensor]).sortBy('timestamp').then(function(array) {
        var k, len1;
        for (k = 0, len1 = array.length; k < len1; k++) {
          result = array[k];
          display.push([new Date(result.timestamp * 1000), result.value, null]);
        }
        return db.predicted.where('[plant+sensor]').equals([plant, sensor]).each(function(result) {
          display.push([new Date(result.timestamp * 1000), null, result.value]);
        }).then(function(result) {
          var g;
          smoothPlotter.smoothing = 0.33;
          g = new Dygraph(document.getElementById("graph"), display, {
            labels: ['time', graphName, 'prediction'],
            plotter: smoothPlotter,
            legend: 'always',
            animatedZooms: true
          });
        })["catch"](function(error) {
          console.log(error);
        });
      })["catch"](function(error) {
        console.log(error);
      });
    })["catch"](function(error) {
      console.log(error);
    });
  };

  initLineGraph = function(graphName) {
    var collection_count, db, plant, sensor;
    sensor = getCurrentSensor();
    plant = getCurrentPUUID();
    db = new Dexie('sensordata');
    db.version(1).stores({
      real: '++id, sensor, plant, timestamp, [plant+sensor]',
      predicted: '++id, sensor, plant, [plant+sensor]'
    });
    db.open()["catch"](function() {
      return alert('Uh oh : ' + error);
    });
    collection_count = -1;
    db.real.where('[plant+sensor]').equals([plant, sensor]).count().then(function(result) {
      var count, display;
      display = [];
      console.log(result);
      if (result === 0) {
        display = [];
        console.log('building indexedDB [partial]');
        count = $.ajax({
          url: '/get/plant/sensor/data/count',
          method: 'POST',
          data: {
            'sensor': sensor
          }
        });
        count.done(function(msg) {
          var g, i, prediction, sensordata, start, stop;
          count = JSON.parse(msg)['count'];
          i = 0;
          start = 0;
          stop = 0;
          while (stop < count) {
            i += 1;
            start = i === 1 ? 0 : stop;
            stop = Math.floor(Math.pow(i, 2.8));
            console.log(stop - start);
            if (i === 1) {
              smoothPlotter.smoothing = 0.33;
              g = new Dygraph(document.getElementById("graph"), display, {
                labels: ['time', graphName, 'prediction'],
                plotter: smoothPlotter,
                legend: 'always',
                animatedZooms: true
              });
            }
            sensordata = $.ajax({
              url: '/get/plant/sensor/data/range',
              method: 'POST',
              data: {
                'sensor': sensor,
                'start': start,
                'stop': stop
              }
            });
            sensordata.done(function(sensordatamsg) {
              var bulkadd, data, j, json_msg, len;
              bulkadd = [];
              json_msg = JSON.parse(sensordatamsg);
              for (j = 0, len = json_msg.length; j < len; j++) {
                data = json_msg[j];
                display.unshift([new Date(data['timestamp'] * 1000), data['value'], null]);
                bulkadd.push({
                  plant: plant,
                  sensor: sensor,
                  value: data['value'],
                  timestamp: data['timestamp']
                });
              }
              display.sort(function(a, b) {
                return a[0] - b[0];
              });
              db.real.bulkAdd(bulkadd).then(function(result) {
                g.updateOptions({
                  'file': display
                });
              })["catch"](function(error) {
                console.log(error);
              });
            });
          }
          prediction = $.ajax({
            url: '/get/plant/sensor/prediction',
            method: 'POST',
            data: {
              'sensor': sensor
            }
          });
          prediction.done(function(prediction) {
            var bulkadd, data, j, json_prediction, len;
            json_prediction = JSON.parse(prediction);
            bulkadd = [];
            console.log('predicting');
            for (j = 0, len = json_prediction.length; j < len; j++) {
              data = json_prediction[j];
              display.push([new Date(data['timestamp'] * 1000), null, data['value']]);
              bulkadd.push({
                plant: plant,
                sensor: sensor,
                value: data['value'],
                timestamp: data['timestamp']
              });
            }
            return db.predicted.bulkAdd(bulkadd).then(function(result) {
              g.updateOptions({
                'file': display
              });
            });
          });
          return;
        });
        return;
      } else {
        console.log('using indexedDB');
        db.real.where('[plant+sensor]').equals([plant, sensor]).reverse().sortBy('timestamp').then(function(result) {
          var latestdata;
          result = result[0];
          latestdata = $.ajax({
            url: '/get/plant/sensor/dataset/custom',
            method: 'POST',
            data: {
              'latest_timestamp': result['timestamp']
            }
          });
          latestdata.done(function(msg) {
            var bulkadd, entry, j, jsonmsg, len, ref;
            display = [];
            jsonmsg = JSON.parse(msg);
            console.log(jsonmsg['real'].length);
            bulkadd = [];
            ref = jsonmsg['real'];
            for (j = 0, len = ref.length; j < len; j++) {
              entry = ref[j];
              bulkadd.push({
                plant: plant,
                sensor: sensor,
                value: entry['value'],
                timestamp: entry['timestamp']
              });
            }
            return db.real.bulkAdd(bulkadd).then(function(result) {
              bulkadd = [];
              console.log(jsonmsg['predicted'].length);
              if (jsonmsg['predicted'].length > 0) {
                db.predicted.clear().then(function(result) {
                  console.log('terminating predicted table');
                  return setuppredicted(db, jsonmsg, plant, sensor, graphName);
                });
              } else {
                console.log('continuing');
                setuppredicted(db, jsonmsg, plant, sensor, graphName);
              }
            })["catch"](function(error) {
              console.log(error);
            });
          });
        })["catch"](function(error) {
          console.log(error);
        });
      }
    })["catch"](function(error) {
      console.log(error);
    });
  };

  window.initLineGraph = initLineGraph;

  initSetTab = function(tabName) {
    $('div.menu.mainMenu').children('.' + tabName).addClass('active');
  };

  window.initSetTab = initSetTab;

  sg_nsps = function() {
    var request;
    request = $.ajax({
      url: '/get/plant/settings/data/non_specific',
      method: 'POST',
      data: {}
    });
    request.done(function(msg) {
      msg = JSON.parse(msg);
      $('#__nsps_name input').val(msg['name']);
      $('#__nsps_type input').val(msg['type']);
      $('#__nsps_location input').val(msg['location']);
      $('#__nsps_segment').fadeIn('slow');
    });
  };

  window.sg_nsps = sg_nsps;

  sg_nsps_reset = function(that) {
    $(that).addClass('disabled');
    $(that).addClass('loading');
    sg_nsps();
    $(document).ajaxComplete(function() {
      $(that).removeClass('disabled');
      return $(that).removeClass('loading');
    });
  };

  window.sg_nsps_reset = sg_nsps_reset;

  sg_nsps_submit = function(that) {
    var request;
    $(that).addClass('disabled');
    $(that).addClass('loading');
    request = $.ajax({
      url: '/update/plant/settings/non_specific',
      method: 'POST',
      data: {
        'name': $('#__nsps_name input').val(),
        'location': $('#__nsps_location input').val(),
        'type': $('#__nsps_type input').val()
      }
    });
    return request.done(function(msg) {
      msg = JSON.parse(msg);
      $(that).removeClass('disabled');
      $(that).removeClass('loading');
      if (msg['info'] === 'change') {
        return window.location = '/plant/' + msg['plant'] + '/overview';
      }
    });
  };

  window.sg_nsps_submit = sg_nsps_submit;

  sg_ssps = function() {
    var request;
    request = $.ajax({
      url: '/get/plant/settings/data/sensor_ranges',
      method: 'POST',
      data: {}
    });
    request.done(function(msg) {
      var item, j, len, range_request, settings;
      msg = JSON.parse(msg);
      for (j = 0, len = msg.length; j < len; j++) {
        item = msg[j];
        settings = item['settings'];
        range_request = $.ajax({
          url: '/get/sensor/range',
          method: 'POST',
          data: {
            'sensor': item['sensor']
          },
          async: false
        });
        range_request.done(function(range) {
          var current_settings, data, sensor;
          data = JSON.parse(range);
          range = data['range'];
          sensor = data['sensor'];
          current_settings = [];
          current_settings.push(settings['yellow']['min']);
          current_settings.push(settings['green']['min']);
          current_settings.push(settings['green']['max']);
          current_settings.push(settings['yellow']['max']);
          return $("#flat-slider-vertical-" + sensor).slider({
            max: range['max'],
            min: range['min'],
            values: current_settings,
            orientation: "vertical"
          }).slider("pips", {
            first: "pip",
            last: "pip"
          }).slider("float");
        });
      }
      $('.__ssps_segment').fadeIn('slow');
    });
  };

  window.sg_ssps = sg_ssps;

  sg_ssps_submit = function(that) {
    var name, request, values;
    $(that).addClass('disabled');
    $(that).addClass('loading');
    name = $(that).parent().parent().parent().attr('class').split(' ')['2'].split('_')[1];
    values = $("#flat-slider-vertical-" + name).slider("values");
    values = values.sort(function(a, b) {
      return a - b;
    });
    $("#flat-slider-vertical-" + name).slider("values", values);
    request = $.ajax({
      url: '/update/plant/ranges',
      method: 'POST',
      data: {
        'new': values,
        'sensor': name
      }
    });
    request.done(function(msg) {
      $(that).removeClass('disabled');
      return $(that).removeClass('loading');
    });
  };

  window.sg_ssps_submit = sg_ssps_submit;

  sg_ssps_reset = function(that) {
    var name, request;
    $(that).addClass('disabled');
    $(that).addClass('loading');
    name = $(that).parent().parent().parent().attr('class').split(' ')['2'].split('_')[1];
    request = $.ajax({
      url: '/get/plant/sensor/ranges',
      method: 'POST',
      data: {
        'sensor': name
      }
    });
    request.done(function(msg) {
      var values;
      msg = JSON.parse(msg);
      values = [];
      values.push(msg['yellow']['min']);
      values.push(msg['green']['min']);
      values.push(msg['green']['max']);
      values.push(msg['yellow']['max']);
      $("#flat-slider-vertical-" + name).slider("values", values);
      $(that).removeClass('disabled');
      $(that).removeClass('loading');
    });
  };

  window.sg_ssps_reset = sg_ssps_reset;

  sg_rsps = function() {
    var request;
    request = $.ajax({
      url: '/get/responsibles',
      method: 'POST',
      data: {}
    });
    request.done(function(msg) {
      var current, j, len, person;
      msg = JSON.parse(msg);
      for (j = 0, len = msg.length; j < len; j++) {
        person = msg[j];
        $('#select').append('<option value="' + person['email'] + '">' + person['name'] + '</option>');
      }
      current = $.ajax({
        url: '/get/plant/responsible',
        method: 'POST',
        data: {}
      });
      return current.done(function(msg) {
        msg = JSON.parse(msg);
        $('#select').dropdown('set selected', msg['email']);
        $('#__rsps_input').val(msg['email']);
        $('#__rsps_segment').fadeIn('slow');
      });
    });
  };

  window.sg_rsps = sg_rsps;

  sg_rsps_change = function(that) {
    $('#__rsps_input').val($(that).val());
  };

  window.sg_rsps_change = sg_rsps_change;

  sg_rsps_submit = function(that) {
    var email, name, request;
    $(that).addClass('disabled');
    $(that).addClass('loading');
    name = $("#select option:selected").text();
    email = $('#__rsps_input').val();
    request = $.ajax({
      url: '/update/plant/responsible',
      method: 'POST',
      data: {
        'name': name,
        'email': email
      }
    });
    request.done(function(msg) {
      $(that).removeClass('disabled');
      $(that).removeClass('loading');
    });
  };

  window.sg_rsps_submit = sg_rsps_submit;

  sg_rsps_create = function(that) {
    var email, name, request, wizard;
    $(that).addClass('disabled');
    $(that).addClass('loading');
    wizard = $("#create_select option:selected").text();
    console.log(wizard);
    name = $('#__rspsc_name').val();
    email = $('#__rspsc_email').val();
    request = $.ajax({
      url: '/create/responsible',
      method: 'POST',
      data: {
        'name': name,
        'email': email,
        'wizard': wizard
      }
    });
    request.done(function(msg) {
      $(that).removeClass('disabled');
      $(that).removeClass('loading');
    });
  };

  window.sg_rsps_create = sg_rsps_create;

  sg_rsps_reset = function(that) {
    var current;
    $(that).addClass('disabled');
    $(that).addClass('loading');
    current = $.ajax({
      url: '/get/plant/responsible',
      method: 'POST',
      data: {}
    });
    return current.done(function(msg) {
      msg = JSON.parse(msg);
      $('#select').dropdown('set selected', msg['email']);
      $('#__rsps_input').val(msg['email']);
      $(that).removeClass('disabled');
      $(that).removeClass('loading');
    });
  };

  window.sg_rsps_reset = sg_rsps_reset;

  device_discover = function() {
    var current;
    $('div.ui.selection.dropdown.discover > div.default.text').html('please wait a couple of seconds');
    current = $.ajax({
      url: '/get/discover',
      method: 'POST',
      data: {}
    });
    current.done(function(msg) {
      var item, j, len;
      msg = JSON.parse(msg);
      $('div.ui.selection.dropdown.discover > div.menu').empty();
      for (j = 0, len = msg.length; j < len; j++) {
        item = msg[j];
        if (msg['master'] === true) {
          msg['role'] = 'master';
        } else {
          msg['role'] = 'slave';
        }
        $('div.ui.selection.dropdown.discover > div.menu').append('<div class="item ' + msg['role'] + '" data-value="' + msg['ip'] + '"> ' + msg['ip'] + ' </div>');
      }
      return $('div.ui.selection.dropdown.discover > div.default.text').html('IP-Adress - done loading');
    });
  };

  window.device_discover = device_discover;

  device_master = function() {
    var current;
    $('div.ui.selection.dropdown.master > div.default.text').html('please wait a couple of seconds');
    current = $.ajax({
      url: '/get/master',
      method: 'POST',
      data: {}
    });
    current.done(function(msg) {
      var content, item, j, len;
      msg = JSON.parse(msg);
      $('div.ui.selection.dropdown.master > div.menu').empty();
      for (j = 0, len = msg.length; j < len; j++) {
        item = msg[j];
        content = msg['name'] + " <" + msg['ip'] + ">";
        $('div.ui.selection.dropdown.master > div.menu').append("<div class='item' data-value='" + msg['uuid'] + "'>" + content + "</div>");
      }
      $('div.ui.selection.dropdown.master > div.default.text').html('ready for selection');
    });
  };

  window.device_master = device_master;

  add_plant_responsibles = function() {
    var current;
    $('div.ui.selection.dropdown.responsible > div.default.text').html('please wait a couple of seconds');
    current = $.ajax({
      url: '/get/responsibles',
      method: 'POST',
      data: {}
    });
    current.done(function(msg) {
      var j, len, person;
      msg = JSON.parse(msg);
      $('div.ui.selection.dropdown.responsible > div.menu').empty();
      for (j = 0, len = msg.length; j < len; j++) {
        person = msg[j];
        $('div.ui.selection.dropdown.responsible > div.menu').append('<div class="item" data-value="' + person['email'] + '">' + person['name'] + ' &lt' + person['email'] + '&gt </div>');
      }
      return $('div.ui.selection.dropdown.responsible > div.default.text').html('Responsible - done loading');
    });
  };

  window.add_plant_responsibles = add_plant_responsibles;

  register_new_plant = function() {
    var a, b, c, current, d, e, f;
    console.log('HEY');
    a = $('input.name').val();
    b = $('input.location').val();
    c = $('input.species').val();
    d = $('input.notification_interval').val();
    e = $('.ui.selection.dropdown.responsible .active.selected').data()['value'];
    f = $('.ui.selection.dropdown.discover .active.selected').data()['value'];
    current = $.ajax({
      url: '/create/plant',
      method: 'POST',
      data: {
        'name': a,
        'location': b,
        'species': c,
        'interval': d,
        'email': e,
        'ip': f
      }
    });
    current.done(function(msg) {
      return window.location.href = '/';
    });
  };

  window.register_new_plant = register_new_plant;

  $(function() {
    $('a.item.add_plant').click(function(e) {
      var request;
      request = $.ajax({
        url: '/display/add_plant/',
        method: 'POST',
        data: {}
      });
      request.done(function(msg) {
        $('section.mainContent').fadeOut('slow', function() {
          $('section.mainContent').html(msg);
          $('section.mainContent').html(msg).fadeIn('slow');
        });
        return window.history.pushState({}, '', '/add_plant');
      });
    });
    $('div.menu.mainMenu a').click(function(e) {
      $(this).parent().children('.active').removeClass('active');
      $(this).addClass('active');
    });
    $('a.item.global_settings').click(function(e) {
      var request;
      request = $.ajax({
        url: '/get/general/settings',
        method: 'POST',
        data: {}
      });
      request.done(function(msg) {
        $('section.mainContent').html(msg);
        window.history.pushState({}, '', '/global/settings');
        $('div.menu.mainMenu a').parent().children('.active').removeClass('active');
        $('div.pusher div.ui.segment div.information h1.ui.header.plant_header').html(_.capitalize('Global Settings'));
        $('div.iopheader div.ui.menu.secondary').css('display', 'none');
      });
      request.fail(function(jqXHR, textStatus) {
        $('section.mainContent').html('Request failed:' + textStatus);
      });
      window.history.pushState({}, '', '/global/settings');
    });
    $('a.item.plant_settings').click(function(e) {
      var request;
      request = $.ajax({
        url: '/get/plant/settings',
        method: 'POST',
        data: {}
      });
      request.done(function(msg) {
        $('section.mainContent').html(msg);
        $('div.menu.mainMenu a').parent().children('.active').removeClass('active');
      });
      request.fail(function(jqXHR, textStatus) {
        $('section.mainContent').html('Request failed:' + textStatus);
      });
      window.history.pushState({}, '', '/plant/' + getCurrentPlant() + '/settings');
    });
    $('a.item.plant').click(function(e) {
      var plant, request;
      plant = $(this).attr('class').split(' ')[2];
      request = $.ajax({
        url: '/get/plant/overview',
        method: 'POST',
        data: {
          plant: plant
        }
      });
      request.done(function(msg) {
        $('section.mainContent').fadeOut('slow', function() {
          $('section.mainContent').html(msg).fadeIn('slow');
        });
        window.history.pushState({}, '', '/plant/' + plant + '/overview');
        $('div.menu.mainMenu a').parent().children('.active').removeClass('active');
        $('div.menu.mainMenu a.overview').addClass('active');
        $('div.pusher div.ui.segment div.information h1.ui.header.plant_header').html(_.capitalize(plant));
        $('div.iopheader div.ui.menu.secondary').css('display', 'inherit');
      });
      request.fail(function(jqXHR, textStatus) {
        $('section.mainContent').html('Request failed:' + textStatus);
      });
    });
    $('a.item.sensor').click(function(e) {
      var request, sensor;
      sensor = $(this).attr('class').split(' ')[2];
      request = $.ajax({
        url: '/get/plant/sensor',
        method: 'POST',
        data: {
          sensor: sensor
        }
      });
      request.done(function(msg) {
        $('section.mainContent').html(msg);
      });
      request.fail(function(jqXHR, textStatus) {
        $('section.mainContent').html('Request failed:' + textStatus);
      });
      window.history.pushState({}, '', '/plant/' + getCurrentPlant() + '/' + sensor);
    });
    $('a.item.overview').click(function(e) {
      var request;
      request = $.ajax({
        url: '/get/plant/overview',
        method: 'POST',
        data: {}
      });
      request.done(function(msg) {
        $('section.mainContent').html(msg);
        window.history.pushState({}, '', '/plant/' + getCurrentPlant() + '/overview');
      });
      request.fail(function(jqXHR, textStatus) {
        $('section.mainContent').html('Request failed:' + textStatus);
      });
    });
  });

}).call(this);
