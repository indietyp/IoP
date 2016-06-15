(($) ->

  $.fn.drawDoughnutChart = (value, max_min_range, ranges, options) ->
    if value < 0
      limiter = Math.abs(max_min_range['min']) - Math.abs(value)
      limiter = 0 if value > max_min_range['min']
      data = [
        { title: "--", value : Math.abs(limiter),  color: "#000000" },
        { title: "--", value : Math.abs(value),  color: "#2C3E50" },
      ]
    else
      limiter = max_min_range['max'] - value
      console.log(limiter)
      console.log(value)
      data = [
        { title: "--", value : value,  color: "#2C3E50" },
        { title: "--", value : limiter,  color: "#000000" },
      ]
    $this = this
    W = $this.width()
    H = $this.height()
    centerX = W / 2
    centerY = H / 2
    cos = Math.cos
    sin = Math.sin
    PI = Math.PI
    settings = $.extend({
      segmentShowStroke: true
      segmentStrokeColor: '#0C1013'
      segmentStrokeWidth: 1
      baseColor: 'rgba(0,0,0,0.5)'
      baseOffset: 4
      edgeOffset: 10
      percentageInnerCutout: 75
      animation: true
      animationSteps: 45
      animationEasing: 'easeInOutExpo'
      animateRotate: true
      tipOffsetX: -8
      tipOffsetY: -45
      tipClass: 'doughnutTip'
      summaryClass: 'doughnutSummary'
      summaryTitle: 'Derzeit:'
      summaryTitleClass: 'doughnutSummaryTitle'
      summaryNumberClass: 'doughnutSummaryNumber'
      beforeDraw: ->
      afterDrawed: ->

    }, options)
    animationOptions =
      linear: (t) ->
        t
      easeInOutExpo: (t) ->
        v = if t < .5 then 8 * t * t * t * t else 1 - (8 * --t * t * t * t)
        if v > 1 then 1 else v
    requestAnimFrame = do ->
      window.requestAnimationFrame or window.webkitRequestAnimationFrame or window.mozRequestAnimationFrame or window.oRequestAnimationFrame or window.msRequestAnimationFrame or (callback) ->
        window.setTimeout callback, 1000 / 60
        return
    #Functions

    getHollowCirclePath = (doughnutRadius, cutoutRadius) ->
      #Calculate values for the path.
      #We needn't calculate startRadius, segmentAngle and endRadius, because base doughnut doesn't animate.
      startRadius = -1.570
      segmentAngle = 6.2831
      endRadius = 4.7131
      startX = centerX + cos(startRadius) * doughnutRadius
      startY = centerY + sin(startRadius) * doughnutRadius
      endX2 = centerX + cos(startRadius) * cutoutRadius
      endY2 = centerY + sin(startRadius) * cutoutRadius
      endX = centerX + cos(endRadius) * doughnutRadius
      endY = centerY + sin(endRadius) * doughnutRadius
      startX2 = centerX + cos(endRadius) * cutoutRadius
      startY2 = centerY + sin(endRadius) * cutoutRadius
      cmd = [
        'M'
        startX
        startY
        'A'
        doughnutRadius
        doughnutRadius
        0
        1
        1
        endX
        endY
        'Z'
        'M'
        startX2
        startY2
        'A'
        cutoutRadius
        cutoutRadius
        0
        1
        0
        endX2
        endY2
        'Z'
      ]
      cmd = cmd.join(' ')
      cmd

    # function pathMouseEnter(e) {
    #   var order = $(this).data().order;
    #   $tip.text(data[order].title + ": " + data[order].value)
    #       .fadeIn(200);
    #   settings.onPathEnter.apply($(this),[e,data]);
    # }
    # function pathMouseLeave(e) {
    #   $tip.hide();
    #   settings.onPathLeave.apply($(this),[e,data]);
    # }
    # function pathMouseMove(e) {
    #   $tip.css({
    #     top: e.pageY + settings.tipOffsetY,
    #     left: e.pageX - $tip.width() / 2 + settings.tipOffsetX
    #   });
    # }

    drawPieSegments = (animationDecimal) ->
      startRadius = -PI / 2
      rotateAnimation = 1
      if settings.animation and settings.animateRotate
        rotateAnimation = animationDecimal
      #count up between0~1
      drawDoughnutText animationDecimal, segmentTotal
      $pathGroup.attr 'opacity', animationDecimal
      #If data have only one value, we draw hollow circle(#1).
      if data.length == 1 and 4.7122 < rotateAnimation * data[0].value / segmentTotal * PI * 2 + startRadius
        $paths[0].attr 'd', getHollowCirclePath(doughnutRadius, cutoutRadius)
        return
      i = 0
      len = data.length
      while i < len
        segmentAngle = rotateAnimation * data[i].value / segmentTotal * PI * 2
        endRadius = startRadius + segmentAngle
        largeArc = if (endRadius - startRadius) % PI * 2 > PI then 1 else 0
        startX = centerX + cos(startRadius) * doughnutRadius
        startY = centerY + sin(startRadius) * doughnutRadius
        endX2 = centerX + cos(startRadius) * cutoutRadius
        endY2 = centerY + sin(startRadius) * cutoutRadius
        endX = centerX + cos(endRadius) * doughnutRadius
        endY = centerY + sin(endRadius) * doughnutRadius
        startX2 = centerX + cos(endRadius) * cutoutRadius
        startY2 = centerY + sin(endRadius) * cutoutRadius
        cmd = [
          'M'
          startX
          startY
          'A'
          doughnutRadius
          doughnutRadius
          0
          largeArc
          1
          endX
          endY
          'L'
          startX2
          startY2
          'A'
          cutoutRadius
          cutoutRadius
          0
          largeArc
          0
          endX2
          endY2
          'Z'
        ]
        $paths[i].attr 'd', cmd.join(' ')
        startRadius += segmentAngle
        i++
      return

    drawDoughnutText = (animationDecimal, segmentTotal) ->
      $summaryNumber.css(opacity: animationDecimal).text (data[0].value * animationDecimal).toFixed(1)
      return

    animateFrame = (cnt, drawData) ->
      easeAdjustedAnimationPercent = if settings.animation then CapValue(easingFunction(cnt), null, 0) else 1
      drawData easeAdjustedAnimationPercent
      return

    animationLoop = (drawData) ->
      animFrameAmount = if settings.animation then 1 / CapValue(settings.animationSteps, Number.MAX_VALUE, 1) else 1
      cnt = if settings.animation then 0 else 1
      requestAnimFrame ->
        cnt += animFrameAmount
        animateFrame cnt, drawData
        if cnt <= 1
          requestAnimFrame arguments.callee
        else
          settings.afterDrawed.call $this
        return
      return

    Max = (arr) ->
      Math.max.apply null, arr

    Min = (arr) ->
      Math.min.apply null, arr

    isNumber = (n) ->
      !isNaN(parseFloat(n)) and isFinite(n)

    CapValue = (valueToCap, maxValue, minValue) ->
      if isNumber(maxValue) and valueToCap > maxValue
        return maxValue
      if isNumber(minValue) and valueToCap < minValue
        return minValue
      valueToCap

    settings.beforeDraw.call $this
    $svg = $('<svg width="' + W + '" height="' + H + '" viewBox="0 0 ' + W + ' ' + H + '" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"></svg>').appendTo($this)
    $paths = []
    easingFunction = animationOptions[settings.animationEasing]
    doughnutRadius = Min([
      H / 2
      W / 2
    ]) - (settings.edgeOffset)
    cutoutRadius = doughnutRadius * settings.percentageInnerCutout / 100
    segmentTotal = 0
    #Draw base doughnut
    baseDoughnutRadius = doughnutRadius + settings.baseOffset
    baseCutoutRadius = cutoutRadius - (settings.baseOffset)
    $(document.createElementNS('http://www.w3.org/2000/svg', 'path')).attr(
      'd': getHollowCirclePath(baseDoughnutRadius, baseCutoutRadius)
      'fill': settings.baseColor).appendTo $svg
    #Set up pie segments wrapper
    $pathGroup = $(document.createElementNS('http://www.w3.org/2000/svg', 'g'))
    $pathGroup.attr(opacity: 0).appendTo $svg
    #Set up tooltip
    # var $tip = $('<div class="' + settings.tipClass + '" />').appendTo('body').hide(),
    #     tipW = $tip.width(),
    #     tipH = $tip.height();
    #Set up center text area
    summarySize = (cutoutRadius - (doughnutRadius - cutoutRadius)) * 2
    $summary = $('<div class="' + settings.summaryClass + '" />').appendTo($this).css(
      width: summarySize + 'px'
      height: summarySize + 'px'
      'margin-left': -(summarySize / 2) + 'px'
      'margin-top': -(summarySize / 2) + 'px')
    $summaryTitle = $('<p class="' + settings.summaryTitleClass + '">' + settings.summaryTitle + '</p>').appendTo($summary)
    $summaryNumber = $('<p class="' + settings.summaryNumberClass + '"></p>').appendTo($summary).css(opacity: 0)
    i = 0
    len = data.length
    while i < len
      segmentTotal += data[i].value
      $paths[i] = $(document.createElementNS('http://www.w3.org/2000/svg', 'path')).attr(
        'stroke-width': settings.segmentStrokeWidth
        'stroke': settings.segmentStrokeColor
        'fill': data[i].color
        'data-order': i).appendTo($pathGroup)
      # .on("mouseenter", pathMouseEnter)
      # .on("mouseleave", pathMouseLeave)
      # .on("mousemove", pathMouseMove);
      i++
    #Animation start
    animationLoop drawPieSegments
    $this

  return
) jQuery

# ---
# generated by js2coffee 2.2.0
