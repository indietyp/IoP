(function(){var e,i,n,a,t,s,o,l,d,r,c,u;d=function(e){var i;return console.log("TEST!"),i=$.ajax({url:"/get/notification/message/names",method:"POST",data:{}}),i.done(function(i){var n,a,t,s,o,l;for(i=JSON.parse(i),console.log(i),$(".dropdown.notification_message > .menu").emtpy,n=0,a=i.length;n<a;n++)t=i[n],l=t.uuid,s=t.name,o="<div class='item' data-value='"+l+"'>"+s+"</div>",console.log(o),$(".dropdown.notification_message > .menu").append(o);return e("finished")})},window.get_notification_messages=d,t=function(e){var i;void 0!==e&&($(e).addClass("disabled"),$(e).addClass("loading")),i=$.ajax({url:"/get/plant/notification/message",method:"POST"}),i.done(function(i){if(i=JSON.parse(i),$(".notification_message_content").val(i.message),$(".ui.selection.dropdown").dropdown("set selected",i.uuid),void 0!==e)return $(e).removeClass("disabled"),$(e).removeClass("loading")})},window.get_current_notification_message=t,l=function(e){var i;return i=$.ajax({url:"/get/notification/message/content",method:"POST",data:{uuid:e}}),i.done(function(e){return e=JSON.parse(e),$(".notification_message_content").val(e)})},window.get_notification_message_content=l,u=function(e,i,n,a,t){var s,o;return null==t&&(t=!0),$(e).addClass("disabled"),$(e).addClass("loading"),s={message:i,name:n},s.responsible=t,a===!0&&(s.uuid=a),o=$.ajax({url:"/submit/notification/message",method:"POST",data:s}),o.done(function(i){return i=JSON.parse(i),"ok"!==i.code&&($(".alert").html=i.code),$(e).removeClass("disabled"),$(e).removeClass("loading")})},window.submit_notification_message=u,o=function(){var e;return e=$.ajax({url:"/get/responsibles",method:"POST"}),e.done(function(e){var i,n,a,t,s,o;for(e=JSON.parse(e),$(".ui.middle.aligned.divided.list").html(""),s=[],i=0,n=e.length;i<n;i++)a=e[i],o='<div class="item"> <div class="right floated content"> <div class="ui small basic icon buttons"> <button class="ui button"> <div class="ui radio checkbox"> <input type="radio" name="wizard" [[checked]] onChange="change_wizard_general_settings_responsible(this, \'[[identifier]]\')"> <label><i class="wizard icon"></i> </label> </div> </button> <button onclick="$(\'.[[identifier]]\').accordion(\'toggle\', 0);" class="ui button"><i class="edit icon"></i> </button> <button class="ui button" onclick="delete_general_settings_responsible(\'[[identifier]]\')"><i class="remove icon"></i> </button> </div> </div><img src="https://source.unsplash.com/category/nature" class="ui avatar image"> <div class="content">[[name]]</div> <div class="ui accordion [[identifier]]"> <div style="height:0;padding:0" class="title"></div> <div style="margin-top:1%" class="content"> <div class="ui grid"> <div class="two column row relaxed"> <div style="margin-bottom:1%" class="column"> <div class="ui fluid left icon input"> <input type="text" class="name-[[identifier]]" placeholder="Name" value="[[name]]"><i class="tag icon"></i> </div> </div> <div class="column"> <div class="ui fluid left icon input"> <input type="text" class="email-[[identifier]]" placeholder="EMail" value="[[email]]"><i class="mail icon"></i> </div> </div> </div> </div> <div class="ui two buttons"> <div class="ui basic button fluid green" onclick="change_information_general_settings_responsible(this, \'[[identifier]]\')">Apply</div> <div class="ui basic button fluid red">Reset</div> </div> </div> </div> <script type="text/javascript"> </script> </div>',o=o.replace(/\[\[identifier\]\]/g,a.uuid),o=o.replace(/\[\[name\]\]/g,a.name),o=o.replace(/\[\[email\]\]/g,a.email),t=a.wizard===!1?"":"checked",o=o.replace(/\[\[checked\]\]/g,t),s.push($(".ui.middle.aligned.divided.list").append(o));return s})},window.get_general_settings_responsibles=o,a=function(e){var i;i=$.ajax({url:"/remove/responsible",method:"POST",data:{uuid:e}}),i.done(function(e){e=JSON.parse(e),console.log(e),o()})},window.delete_general_settings_responsible=a,i=function(e,i){var n;e.checked&&(n=$.ajax({url:"/change/responsible/wizard",method:"POST",data:{uuid:i}}),n.done(function(e){e=JSON.parse(e),console.log(e),o()}))},window.change_wizard_general_settings_responsible=i,e=function(e,i){var n,a,t;$(e).addClass("disabled"),$(e).addClass("loading"),a=$(".name-"+i).val(),n=$(".email-"+i).val(),t=$.ajax({url:"/change/responsible",method:"POST",data:{uuid:i,name:a,email:n}}),t.done(function(i){i=JSON.parse(i),console.log(i),$(e).removeClass("disabled"),$(e).removeClass("loading"),o()})},window.change_information_general_settings_responsible=e,n=function(){var e,i,n;i=$(".new.name").val(),e=$(".new.email").val(),n=$.ajax({url:"/create/responsible/none",method:"POST",data:{name:i,email:e,wizard:"no"}}),n.done(function(e){return e=JSON.parse(e),console.log(e),$(".new.name").val(""),$(".new.email").val(""),o()})},window.create_new_general_settings_responsible=n,c=function(e){var i;$(e).addClass("disabled"),$(e).addClass("loading"),i=$.ajax({url:"/change/plant/intervals",method:"POST",data:{notification:$("#flat-slider-general-interval").slider("option","value"),connection:$("#flat-slider-dead-interval").slider("option","value"),non_persistant:$("#flat-slider-non-persistant-interval").slider("option","value")}}),i.done(function(i){return i=JSON.parse(i),$(e).removeClass("disabled"),$(e).removeClass("loading")})},window.modify_plant_durations=c,s=function(){var e;e=$.ajax({url:"/get/day_night",method:"POST"}),e.done(function(e){var i,n;return e=JSON.parse(e),e.ledbar&&$(".field.ledbar > .ui.checkbox > input").prop("checked",!0),e.display&&$(".field.display > .ui.checkbox > input").prop("checked",!0),e.generalleds&&$(".field.generalleds > .ui.checkbox > input").prop("checked",!0),e.notification&&$(".field.notification > .ui.checkbox > input").prop("checked",!0),i=e.start.toString(),i=3===i.length?i.slice(0,1):i.slice(0,2),n=e.stop.toString(),n=3===n.length?n.slice(0,1):n.slice(0,2),$("#flat-slider-time-interval").slider({max:24,min:0,range:!0,values:[parseInt(i),parseInt(n)]}).slider("pips",{first:"pip",last:"pip"})})},window.get_day_night=s,r=function(e){var i,n;$(e).addClass("disabled"),$(e).addClass("loading"),n=$("#flat-slider-time-interval").slider("option","values"),i=$.ajax({url:"/change/day_night",method:"POST",data:{stop:parseInt(n[1].toString()+"00"),start:parseInt(n[0].toString()+"00"),ledbar:$(".field.ledbar > .ui.checkbox > input").prop("checked"),display:$(".field.display > .ui.checkbox > input").prop("checked"),generalleds:$(".field.generalleds > .ui.checkbox > input").prop("checked"),notification:$(".field.notification > .ui.checkbox > input").prop("checked")}}),i.done(function(i){return i=JSON.parse(i),$(e).removeClass("disabled"),$(e).removeClass("loading")})},window.modify_day_night=r}).call(this);