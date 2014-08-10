var dashboard = dashboard || {};
var winW = 630, winH = 460;
if (document.body && document.body.offsetWidth) {
 winW = document.body.offsetWidth;
 winH = document.body.offsetHeight;
}
if (document.compatMode=='CSS1Compat' &&
    document.documentElement &&
    document.documentElement.offsetWidth ) {
 winW = document.documentElement.offsetWidth;
 winH = document.documentElement.offsetHeight;
}
if (window.innerWidth && window.innerHeight) {
 winW = window.innerWidth;
 winH = window.innerHeight;
}

$(document)
  .ready(function () {
    start();

    function start() {
      readconfig(init)
    }

    function readconfig(next) {
      $.ajax({
        url: "/st/config.json",
        dataType: "json"
      })
        .success(function (data) {
          dashboard.config = data;
          if (next) {
            next();
          }
        })
        .fail(function (err) {
          console.log("error loading config.json");
          console.log(err)
          // TODO: show the user that something happened
        })
    }

    function init() {
      $("#loadinganimation").show();
      dashboard.campaign_urn = oh.utils.state()[0];
      raw_data = $('#raw_csv_data').text();
      parsed_csv = oh.utils.parsecsv(raw_data);
      loaddata(parsed_csv);
      if (hasdata()) {
        initcharts();
        loadgui();
      }
    }

    function loaddata(records) {
      dashboard.data = crossfilter(records);
      dashboard.dim = {
        main: dashboard.data.dimension(
          oh.utils.get(
            dashboard.config["item_main"]))
      };
      dashboard.groups = {
        all: dashboard.data.groupAll()
      }
    }

    function hasdata() {
      if (dashboard.groups.all.value() == 0) {
        alert("Campaign '" + dashboard.campaign_urn + '" has no responses! Try again later (or press F5)');
        return false
      }
      return true
    }

    function loadgui() {
      $(".hoverinfo").css({
        left: ($(window)
          .width() - $(".hoverinfo")
          .width()) / 2,
        right: ""
      });
      dc.renderAll();
      $("head title").text(dashboard.config.title);
      if (oh.utils.state()[1]) {
        var myhash = +oh.utils.state()[1];
        var alldata = dashboard.dim.main.top(9999);
        var allhashes = $.map(alldata, function (d) {
          return d.hash
        });
        var i = $.inArray(myhash, allhashes);
        if (i > -1) {
          dashboard.modal.showmodal(alldata[i])
        } else {
          oh.utils.state(oh.utils.state()[0])
        }
      }
    }
  });

function initcharts() {
  dashboard.renderlet = function () {
    var funstack = [];

    function call() {
      $.each(funstack, function (index, value) {
        value()
      })
    }

    function register(newfun, delay) {
      if (!delay) {
        funstack.push(newfun)
      } else {
        funstack.push(_.debounce(newfun, delay))
      }
    }

    var init = _.once(function (renderlet) {
      renderlet(call);
    });
    return {
      init: init,
      register: register
    }
  }();
  dc.constants.EVENT_DELAY = 5;
  dashboard.charts = dashboard.charts || {};
  $(dashboard.config.datecharts)
    .each(function (index, conf) {
      $("#calendarpanel").datechart(conf)
    });
  $(dashboard.config.hourcharts)
    .each(function (index, conf) {
      $("#calendarpanel").hourchart(conf)
    });
  $(dashboard.config.smallpiecharts)
    .each(function (index, conf) {
      $("#smallpiepanel").smallpiechart(conf)
    });
  $(dashboard.config.mediumpiecharts)
    .each(function (index, conf) {
      $("#mediumpiepanel").mediumpiechart(conf)
    });
  $(dashboard.config.bigpiecharts)
    .each(function (index, conf) {
      $("#bigpiepanel").bigpiechart(conf)
    });
  $(dashboard.config.jumbopiecharts)
    .each(function (index, conf) {
      $("#jumbopiepanel").jumbopiechart(conf)
    });
  $(dashboard.config.barcharts)
    .each(function (index, conf) {
      $("#histpanel").barchart(conf)
    });
  $(dashboard.config.wordclouds)
    .each(function (index, conf) {
      $("#wcpanel").wordcloud(conf)
    });
  $("#infodiv").filtercount();
  $("#calendarpanel").show();
  $("#jumbopiepanel").show();
  $("#bigpiepanel").show();
  $("#mediumpiepanel").show();
  $("#smallpiepanel").show();
  $("#histpanel").show();
  $("#wcpanel").show();
}
var oh = oh || {};
oh.utils = oh.utils || {};
oh.user = oh.user || {};
oh.utils.getRandomSubarray = function (arr, size) {
  var shuffled = arr.slice(0),
    i = arr.length,
    temp, index;
  while (i--) {
    index = Math.floor(i * Math.random());
    temp = shuffled[index];
    shuffled[index] = shuffled[i];
    shuffled[i] = temp
  }
  return shuffled.slice(0, size)
};
oh.utils.delayexec = function () {
  var timer;

  function exec(call, delay) {
    if (timer) {
      clearTimeout(timer)
    }
    timer = setTimeout(function () {
      timer = null;
      call()
    }, delay);
  }

  return exec
};
oh.utils.parsedate = function (datestring) {
  if (!datestring) {
    return null
  }
  var a = datestring.split(/[^0-9]/);
  return new Date(a[0], a[1] - 1, a[2], a[3], a[4], a[5])
};
oh.utils.get = function (item) {
  return function (d) {
    if (d[item] && d[item] != "NOT_DISPLAYED") {
      return d[item]
    }
    return "NA"
  }
};
oh.utils.getnum = function (item) {
  return function (d) {
    if (d[item] && d[item] != "NOT_DISPLAYED") {
      return parseFloat(d[item]) || null
    }
  }
};
oh.utils.getdate = function (item) {
  return function (d) {
    if (d[item] && d[item] != "NOT_DISPLAYED") {
      return d3.time.day(oh.utils.parsedate(d[item]))
    }
  }
};
oh.utils.bin = function (binwidth) {
  return function (x) {
    return Math.floor(x / binwidth) * binwidth
  }
};
oh.utils.gethour = function (item) {
  return function (d) {
    if (d[item] && d[item] != "NOT_DISPLAYED") {
      return oh.utils.parsedate(d[item])
        .getHours()
    }
  }
};
oh.utils.state = function (mycampaign, myresponse) {
  if (!mycampaign) {
    return window.location.hash.substring(1)
      .split("/")
  }
  if (!myresponse) {
    window.location.hash = mycampaign;
    return
  }
  window.location.hash = mycampaign + "/" + myresponse
};
oh.utils.readconfig = function (next) {
  $.ajax({
    url: "config.json",
    dataType: "json"
  })
    .success(function (data) {
      dashboard.config = data;
      if (next) next()
    })
    .fail(function (err) {
      alert("error loading chart config, please alert Ian on Google+");
      console.log(err)
    })
};
oh.utils.error = function (msg) {
  throw new Error(msg)
};
oh.call = function (path, data, datafun) {
  function processError(errors) {
    if (errors[0].code && errors[0].code == "0200") {
      var pattern = /(is unknown)|(authentication token)|(not provided)/i;
      if (!errors[0].text.match(pattern)) {
        alert(errors[0].text)
      }
    } else {
      alert(errors[0].text)
    }
  }

  var data = data ? data : {};
  data.client = "dashboard";
  var myrequest = $.ajax({
    type: "POST",
    url: "/app" + path,
    data: data,
    dataType: "text",
    xhrFields: {
      withCredentials: true
    }
  })
    .done(function (rsptxt) {
      if (!rsptxt || rsptxt == "") {
        alert("Undefined error.");
        return false
      }
      var response = jQuery.parseJSON(rsptxt);
      if (response.result == "success") {
        if (datafun) datafun(response)
      } else if (response.result == "failure") {
        processError(response.errors);
        return false
      } else {
        alert("JSON response did not contain result attribute.")
      }
    })
    .error(function () {
      alert("Ohmage returned an undefined error.")
    });
  return myrequest
};
oh.campaign_read = function (cb) {
  var req = oh.call("/campaign/read", {
    output_format: "short"
  }, function (res) {
    if (!cb) return;
    var arg = res.metadata && res.metadata.items ? res.metadata.items : null;
    cb(arg)
  });
  return req
};
oh.utils.parsecsv = function (string) {
  var rows = d3.csv.parse(string);
  var records = [];
  rows.forEach(function (d, i) {
    if (d[dashboard.config.item_main] == "NOT_DISPLAYED") return;
    d.hash = murmurhash3_32_gc(JSON.stringify(d));
    records.push(d)
  });
  return records
};
oh.keepalive = _.once(function (t) {
  t = t || 60;
  setInterval(oh.ping, t * 1e3)
});
oh.keepactive = _.once(function (t) {
  $("html").click(function () {
    oh.ping()
  })
});


(function ($) {
  $.fn.smallpiechart = function (options) {
    var target = this;
    var item = options.item;
    var title = options.title || "pie chart";
    var label = options.label || {};
    var chartid = "pie-" + Math.random().toString(36).substring(7);
    dashboard.dim[item] = dashboard.data.dimension(oh.utils.get(item));
    dashboard.groups[item] = dashboard.dim[item].group();
    var mydiv = $("<div/>").addClass("chart").attr("id", chartid);
    var titlediv = $("<div/>").addClass("title").appendTo(mydiv);
    $("<span/>").text(title).appendTo(titlediv);
    titlediv.append("&nbsp;");
    $("<a/>")
      .addClass("reset")
      .attr("href", "#")
      .attr("style", "display:none;")
      .text("(reset)")
      .appendTo(titlediv)
      .on("click", function (e) {
        e.preventDefault();
        mychart.filterAll();
        dc.redrawAll();
        return false
      });
    mydiv.appendTo(target);
    var mychart = dc.pieChart("#" + mydiv.attr("id"))
      .colors(d3.scale.category20())
      .width(200)
      .height(150)
      .radius(50)
      .label(getlabel)
      .dimension(dashboard.dim[item])
      .group(dashboard.groups[item])
      .data(function(group) { return group.all().filter(function(kv) { return kv.value > 0; }); })
      .legend(dc.legend().x(10).y(10));
    dashboard.renderlet.init(mychart.renderlet);
    dashboard.piecharts = dashboard.piecharts || [];
    dashboard.piecharts.push(mychart);
    return target;

    function getlabel(d) {
      return d.value
    }
  }
})(jQuery); // small pie chart


(function ($) {
  $.fn.mediumpiechart = function (options) {
    var target = this;
    var item = options.item;
    var title = options.title || "pie chart";
    var label = options.label || {};
    var chartid = "pie-" + Math.random().toString(36).substring(7);
    dashboard.dim[item] = dashboard.data.dimension(oh.utils.get(item));
    dashboard.groups[item] = dashboard.dim[item].group();
    var mydiv = $("<div/>").addClass("chart").attr("id", chartid);
    var titlediv = $("<div/>").addClass("title").appendTo(mydiv);
    $("<span/>").text(title).appendTo(titlediv);
    titlediv.append("&nbsp;");
    $("<a/>")
      .addClass("reset")
      .attr("href", "#")
      .attr("style", "display:none;")
      .text("(reset)")
      .appendTo(titlediv)
      .on("click", function (e) {
        e.preventDefault();
        mychart.filterAll();
        dc.redrawAll();
        return false
      });
    mydiv.appendTo(target);
    var mychart = dc.pieChart("#" + mydiv.attr("id"))
      .colors(d3.scale.category20())
      .width(250)
      .height(200)
      .radius(80)
      .label(getlabel)
      .dimension(dashboard.dim[item])
      .group(dashboard.groups[item])
      .data(function(group) { return group.all().filter(function(kv) { return kv.value > 0; }); })
      .legend(dc.legend().x(10).y(10));
    dashboard.renderlet.init(mychart.renderlet);
    dashboard.piecharts = dashboard.piecharts || [];
    dashboard.piecharts.push(mychart);
    return target;

    function getlabel(d) {
      return d.value
    }
  }
})(jQuery); // medium pie chart


(function ($) {
  $.fn.bigpiechart = function (options) {
    var target = this;
    var item = options.item;
    var title = options.title || "pie chart";
    var label = options.label || {};
    var chartid = "pie-" + Math.random().toString(36).substring(7);
    dashboard.dim[item] = dashboard.data.dimension(oh.utils.get(item));
    dashboard.groups[item] = dashboard.dim[item].group();
    var mydiv = $("<div/>").addClass("chart").attr("id", chartid);
    var titlediv = $("<div/>").addClass("title").appendTo(mydiv);
    $("<span/>").text(title).appendTo(titlediv);
    titlediv.append("&nbsp;");
    $("<a/>")
      .addClass("reset")
      .attr("href", "#")
      .attr("style", "display:none;")
      .text("(reset)")
      .appendTo(titlediv)
      .on("click", function (e) {
        e.preventDefault();
        mychart.filterAll();
        dc.redrawAll();
        return false
      });
    mydiv.appendTo(target);
    var mychart = dc.pieChart("#" + mydiv.attr("id"))
      .colors(d3.scale.category20())
      .width(450)
      .height(300)
      .radius(100)
      .label(getlabel)
      .dimension(dashboard.dim[item])
      .group(dashboard.groups[item])
      .data(function(group) { return group.all().filter(function(kv) { return kv.value > 0; }); })
      .legend(dc.legend().x(10).y(10));
    dashboard.renderlet.init(mychart.renderlet);
    dashboard.piecharts = dashboard.piecharts || [];
    dashboard.piecharts.push(mychart);
    return target;

    function getlabel(d) {
      return d.value
    }
  }
})(jQuery); // big pie chart


(function ($) {
  $.fn.jumbopiechart = function (options) {
    var target = this;
    var item = options.item;
    var title = options.title || "pie chart";
    var label = options.label || {};
    var chartid = "pie-" + Math.random().toString(36).substring(7);
    dashboard.dim[item] = dashboard.data.dimension(oh.utils.get(item));
    dashboard.groups[item] = dashboard.dim[item].group();
    var mydiv = $("<div/>").addClass("chart").attr("id", chartid);
    var titlediv = $("<div/>").addClass("title").appendTo(mydiv);
    $("<span/>").text(title).appendTo(titlediv);
    titlediv.append("&nbsp;");
    $("<a/>")
      .addClass("reset")
      .attr("href", "#")
      .attr("style", "display:none;")
      .text("(reset)")
      .appendTo(titlediv)
      .on("click", function (e) {
        e.preventDefault();
        mychart.filterAll();
        dc.redrawAll();
        return false
      });
    mydiv.appendTo(target);
    var mychart = dc.pieChart("#" + mydiv.attr("id"))
      .colors(d3.scale.category20())
      .width(800)
      .height(400)
      .radius(175)
      .label(getlabel)
      .dimension(dashboard.dim[item])
      .group(dashboard.groups[item])
      .data(function(group) { return group.all().filter(function(kv) { return kv.value > 0; }); })
      .legend(dc.legend().x(10).y(10))
      .cx(400);
    dashboard.renderlet.init(mychart.renderlet);
    dashboard.piecharts = dashboard.piecharts || [];
    dashboard.piecharts.push(mychart);
    return target;

    function getlabel(d) {
      return d.value
    }
  }
})(jQuery); // jumbo pie chart


(function ($) {
  $.fn.barchart = function (options) {
    var target = this;
    var id = "#" + target.attr("id");
    var item = options.item;
    var title = options.title || item;
    var domain = options.domain || [];
    var chartid = "bar-" + Math.random().toString(36).substring(7);
    dashboard.dim[item] = dashboard.data.dimension(oh.utils.getnum(item));
    domain[0] = domain[0] || +dashboard.dim[item].bottom(1)[0][item];
    domain[1] = domain[1] || +dashboard.dim[item].top(1)[0][item];
    var binwidth = options.binwidth || calcbin(domain);
    domain[0] = rounddown(domain[0], binwidth);
    domain[1] = roundup(domain[1], binwidth);
    var centerbars = binwidth == 1;
    if (centerbars) {
      domain[0] = domain[0] - 1;
      domain[1] = domain[1] + 1
    }
    var x_units = (domain[1] - domain[0]) / binwidth;
    dashboard.groups[item] = dashboard.dim[item].group(oh.utils.bin(binwidth));
    var mydiv = $("<div/>").addClass("chart").addClass("histcontainer").attr("id", chartid);
    var titlediv = $("<div/>").addClass("title").appendTo(mydiv);
    $("<span/>").text(title).appendTo(titlediv);
    titlediv.append("&nbsp;");
    $("<a/>")
      .addClass("reset")
      .attr("href", "#")
      .attr("style", "display:none;")
      .text("(reset)")
      .appendTo(titlediv)
      .on("click", function (e) {
        e.preventDefault();
        mychart.filterAll();
        dc.redrawAll();
        return false
      });
    mydiv.appendTo(target);
    mydiv.draggable({
      containment: "body",
      snap: "body",
      snapMode: "inner"
    });
    var plotwidth = rounddown(295 - 30 - 25, x_units);
    var remainder = 295 - 30 - 25 - plotwidth;
    var mychart = dc.barChart("#" + mydiv.attr("id"))
      .width(295)
      .height(130)
      .gap(1 + centerbars)
      .margins({
        top: 10,
        right: 25 + remainder,
        bottom: 20,
        left: 30
      })
      .dimension(dashboard.dim[item])
      .group(dashboard.groups[item])
      .elasticY(true)
      .centerBar(centerbars)
      .xUnits(function () {
        return x_units
      })
      .x(d3.scale.linear()
        .domain(domain)
        .rangeRound([0, plotwidth]))
      .renderHorizontalGridLines(true)
      .renderVerticalGridLines(true);
    mychart.xAxis()
      .tickFormat(d3.format("d"))
      .tickValues(seq(domain[0], domain[1], binwidth));
    dashboard.renderlet.init(mychart.renderlet);
    return target
  };

  function seq(x, y, by) {
    if (!by) by = 1;
    x = rounddown(x, by);
    y = roundup(y, by);
    out = [];
    for (var i = x; i <= y; i = i + by) {
      out.push(i)
    }
    return out
  }

  function roundup(x, y) {
    return Math.ceil(x / y) * y
  }

  function rounddown(x, y) {
    return Math.floor(x / y) * y
  }

  function calcbin(domain, maxbars) {
    if (!maxbars) maxbars = 10;
    var k = [1, 2, 5];
    var bin = 1;
    while (true) {
      for (i = 0; i < k.length; i++) {
        newbin = bin * k[i];
        if (Math.abs(rounddown(domain[0], newbin) - roundup(domain[1], newbin)) / newbin < maxbars + 1) {
          return newbin
        }
      }
      bin = bin * 10
    }
  }
})(jQuery); // bar chart
(function ($) {
  $.fn.datechart = function (options) {
    var target = this;
    var id = "#" + target.attr("id");
    var item = options.item;
    var dimname = item + "_date";
    var title = options.title || "Date";
    var chartid = "date-chart";
    dashboard.dim[dimname] = dashboard.data.dimension(oh.utils.getdate(item));
    dashboard.groups[dimname] = dashboard.dim[dimname].group();
    var mydiv = $("<div/>").addClass("chart").attr("id", chartid);
    var titlediv = $("<div/>").addClass("title").appendTo(mydiv);
    $("<span/>").text(title).appendTo(titlediv);
    titlediv.append("&nbsp;");
    $("<a/>")
      .addClass("reset")
      .attr("href", "#")
      .attr("style", "display:none;")
      .text("(reset)")
      .appendTo(titlediv)
      .on("click", function (e) {
        e.preventDefault();
        mychart.filterAll();
        dc.redrawAll();
        return false
      });
    mydiv.appendTo(target);
    var mindate = oh.utils.getdate(item)(dashboard.dim[dimname].bottom(1)[0]);
    var maxdate = oh.utils.getdate(item)(dashboard.dim[dimname].top(1)[0]);
    mindate = new Date(mindate.getFullYear(), mindate.getMonth(), mindate.getDate() - 2);
    maxdate = new Date(maxdate.getFullYear(), maxdate.getMonth(), maxdate.getDate() + 2);
    var ndays = (maxdate - mindate) / (24 * 60 * 60 * 1e3);
    if (ndays < 71) {
      maxdate = new Date(mindate.getFullYear(), mindate.getMonth(), mindate.getDate() + 72)
    }
    if (ndays > 365) {
      mindate = new Date(maxdate.getFullYear(), maxdate.getMonth(), maxdate.getDate() - 181)
    }
    var ndays = Math.round((maxdate - mindate) / (24 * 60 * 60 * 1e3));
    var remainder = (winW - 30) % ndays;
    if (remainder > 90) {
      var remainder = (winW - 30) % Math.floor(ndays / 2)
    }
    var mychart = dc.barChart("#" + mydiv.attr("id"))
      .width(winW * 0.8)
      .height(150)
      .transitionDuration(200)
      .margins({
        top: 10,
        right: remainder,
        bottom: 20,
        left: 30
      })
      .dimension(dashboard.dim[dimname])
      .group(dashboard.groups[dimname])
      .centerBar(false)
      .gap(1)
      .elasticY(true)
      .x(d3.time.scale()
        .domain([mindate, maxdate])
        .rangeRound([ndays]))
      .round(d3.time.day.round)
      .xUnits(d3.time.days)
      .renderHorizontalGridLines(true)
      .renderVerticalGridLines(true);
    dashboard.renderlet.init(mychart.renderlet);
    return target
  }
})(jQuery); // date chart
(function ($) {
  $.fn.hourchart = function (options) {
    var target = this;
    var id = "#" + target.attr("id");
    var item = options.item;
    var dimname = item + "_hour";
    var title = options.title || "Date";
    var chartid = "hour-chart";
    dashboard.dim[dimname] = dashboard.data.dimension(oh.utils.gethour(item));
    dashboard.groups[dimname] = dashboard.dim[dimname].group(Math.floor);
    var mydiv = $("<div/>").addClass("chart").attr("id", chartid);
    var titlediv = $("<div/>").addClass("title").appendTo(mydiv);
    $("<span/>").text(title).appendTo(titlediv);
    titlediv.append("&nbsp;");
    $("<a/>")
      .addClass("reset")
      .attr("href", "#")
      .attr("style", "display:none;")
      .text("(reset)")
      .appendTo(titlediv)
      .on("click", function (e) {
        e.preventDefault();
        mychart.filterAll();
        dc.redrawAll();
        return false
      });
    mydiv.appendTo(target);
    var mychart = dc.barChart("#" + mydiv.attr("id"))
      .width((winH/2) + 100)
      .height(150)
      .transitionDuration(200)
      .margins({
        top: 10,
        right: 25,
        bottom: 20,
        left: 30
      })
      .dimension(dashboard.dim[dimname])
      .group(dashboard.groups[dimname])
      .elasticY(true)
      .centerBar(false)
      .gap(1)
      .round(dc.round.floor)
      .x(d3.scale.linear()
        .domain([0, 24])
        .rangeRound([0, 10 * 24]))
      .renderHorizontalGridLines(true)
      .renderVerticalGridLines(true);
    dashboard.renderlet.init(mychart.renderlet);
    return target
  }
})(jQuery); // hour chart
(function ($) {
  $.fn.wordcloud = function (options) {
    var target = this;
    var id = "#" + target.attr("id");
    var variable = options.item;
    var title = options.title || "";
    var width = options.width || winW/2;
    var height = options.height || 350;
    var font = options.font || "Helvetica";
    var wcdelay = oh.utils.delayexec();
    var chartid = "wc-" + Math.random().toString(36).substring(7);
    var resizable = options.resizable || false;
    var maxwords = options.maxwords || 100;
    var mydim = dashboard.dim[variable] = dashboard.data.dimension(oh.utils.get(variable));
    var mydiv = $("<div/>").addClass("wccontainer").addClass("well").css("height", height).appendTo(target);
    var titlediv = $("<div/>").addClass("title").appendTo(mydiv);
    titlediv.append("&nbsp;");
    $("<span/>").text(title).appendTo(titlediv);

    $("<a/>")
      .addClass("refresh")
      .addClass("hide")
      .text("(refresh)")
      .appendTo(titlediv)
      .on("click", function (e) {
        chartdiv.empty();
        _.delay(update, 300)
      });

    var filterinput = $("<input />")
      .attr("type", "text")
      .attr("placeholder", "filter")
      .appendTo(mydiv)
      .on("keyup", function () {
        filter(this.value);
        dc.redrawAll()
      });

    $("<a/>")
      .addClass("reset")
      .addClass("hide")
      .appendTo(titlediv)
      .on("click", function () {
        setvalue()
      });

    var chartdiv = $("<div/>")
      .addClass("chart")
      .attr("id", chartid)
      .appendTo(mydiv);

    function setvalue(newval) {
      filterinput.val(newval || "");
      filterinput.trigger("keyup")
    }

    function filter(word) {
      var filterfun = word ? function (val) {
        return new RegExp(word, "i")
          .test(val)
      } : null;
      mydim.filter(filterfun)
    }

    function build(words) {
      var fill = d3.scale.category20();
      var minval = words.slice(-1)[0]["size"];
      var maxval = words[0]["size"];
      var logscale = d3.scale.linear()
        .range([18, 30])
        .domain([minval, maxval]);
      d3.layout.cloud()
        .size([width, height])
        .words(words)
        .rotate(function (d) {
          return ~~(Math.random() * 3) * 45 - 45
        })
        .font(font)
        .fontSize(function (d) {
          return logscale(d.size)
        })
        .on("end", function (words) {
          d3.select("#" + chartid)
            .append("svg")
            .attr("width", width)
            .attr("height", height)
            .append("g")
            .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")")
            .selectAll("text")
            .data(words)
            .enter()
            .append("a")
            .on("click", function (d) {
              setvalue(d.text);
              return false
            })
            .append("text")
            .style("font-size", function (d) {
              return d.size + "px"
            })
            .style("font-family", font)
            .style("fill", function (d, i) {
              return fill(i)
            })
            .attr("text-anchor", "middle")
            .attr("transform", function (d) {
              return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")"
            })
            .text(function (d) {
              return d.text
            })
        })
        .start()
    }

    function refresh(fade) {
      if (fade && !chartdiv.is(":empty")) {
        chartdiv.fadeOut(500, function () {
          update()
        })
      } else {
        update()
      }
    }

    function update() {
      var starttime = (new Date)
        .getTime();
      chartdiv.empty();
      var alldata = dashboard.dim.main.top(9999);
      var textarray = alldata.map(function (d) {
        return d[variable]
      });
      var wordcounts = wordmap(textarray.join(" "), maxwords);
      var words = wordcounts.map(function (d) {
        return {
          text: d.key,
          size: d.value
        }
      });
      build(words);
      var enddtime = (new Date).getTime();
      var delta = enddtime - starttime;
      $(chartdiv).fadeIn(500)
    }

    dashboard.renderlet.register(function () {
      if (chartdiv.is(":visible")) {
        refresh()
      }
    }, 500);
    dashboard.wordcloud = dashboard.wordcloud || [];
    dashboard.wordcloud.push(chartdiv);
    mydiv.draggable({
      containment: "body",
      snap: "body",
      snapMode: "inner"
    });
    if (resizable) {
      mydiv.resizable({
        start: function () {
          chartdiv.empty()
        },
        stop: function (event, ui) {
          width = ui.size.width;
          height = ui.size.height;
          update()
        }
      })
    }
    return chartdiv
  };
  wordmap = function () {
    var stopWords = /^(not_displayed|it|the|is|are|was|has|had|do|does|did|a|on|what|in|his|her|for|and|of|I'm|I|that|me|to|as|He|She|him|her|how|my|this|who|when|be|an|we|it's|all|any|not|you|so|he's|she's|with|able|from|will|get|by|but|if|at|don't|can|than)$/i;
    var punctuation = /[!"&()*+,-\.\/:;<=>?\[\\\]^`\{|\}~]+/g;
    var wordSeparators = /[\s\u3031-\u3035\u309b\u309c\u30a0\u30fc\uff70]+/g;
    var discard = /^(@|https?:)/;
    var maxLength = 30;

    function entries(map) {
      var entries = [];
      for (var key in map) entries.push({
        key: key,
        value: map[key]
      });
      return entries
    }

    return function (text, maxwords) {
      var tags = {};
      var cases = {};
      text.split(wordSeparators)
        .forEach(function (word) {
          if (discard.test(word)) return;
          word = word.replace(punctuation, "");
          if (stopWords.test(word.toLowerCase())) return;
          word = word.substr(0, maxLength);
          cases[word.toLowerCase()] = word;
          tags[word = word.toLowerCase()] = (tags[word] || 0) + 1
        });
      tags = entries(tags)
        .sort(function (a, b) {
          return b.value - a.value
        });
      tags.forEach(function (d) {
        d.key = cases[d.key]
      });
      return tags.slice(0, maxwords)
    }
  }()
})(jQuery); // tag cloud
(function ($) {
  $.fn.filtercount = function (options) {
    var titlediv = $("<div/>")
      .addClass("title")
      .addClass("dc-data-count")
      .attr("id", "data-count");
    $("<span/>")
      .addClass("filter-count")
      .appendTo(titlediv);
    titlediv.append(" selected out of ");
    $("<span/>")
      .addClass("total-count")
      .appendTo(titlediv);
    titlediv.append(" records | ");
    $("<a/>")
      .addClass("reset")
      .attr("href", "#")
      .text("(reset all)")
      .appendTo(titlediv)
      .on("click", function (e) {
        e.preventDefault();
        $("#wcpanel .reset")
          .trigger("click");
        if (dashboard.map) dashboard.map.resetall();
        dc.filterAll();
        dc.renderAll();
        return false
      });
    this.append(titlediv);
    dc.dataCount("#data-count")
      .dimension(dashboard.data)
      .group(dashboard.groups.all);
    return this
  }
})(jQuery); // filter counts
