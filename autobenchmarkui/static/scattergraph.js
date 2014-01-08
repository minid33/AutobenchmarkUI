function DrawGraph(drawfunc, json_url, title, graphcontainer, colorkey) {
    var jqxhr = $.getJSON(json_url, function () {
        jqxhr.dataType = 'json'
    })
        .done(function (resultData) {
            if (resultData.empty === false) {
                drawfunc(resultData, title, graphcontainer, colorkey)
            }
            else {
                removediv(graphcontainer)
            }
        })
}

function removediv(graphcontainer){
    $('#' + graphcontainer).remove()
}


function keyvalueToPtConfig(keyvalue) {
    var entry = {
        x: new Date(keyvalue['key']).getTime(),
        y: keyvalue['value'],
        id: keyvalue['id'],
        changelist: keyvalue['changelist'],
        branch: keyvalue['branch']
    };
    return entry
}


function keyvalueToPair(keyvalue) {
    return [new Date(keyvalue['key']).getTime(), keyvalue['value']];
}


function dataToSeries(resultData, colorkey, keyvalueConverter) {
    var series = [];
    for (var resultsetattr in resultData['results']) {
        var data = [];
        var resultset = resultData['results'][resultsetattr]
        for (var ind in resultset) {
            var entry = keyvalueConverter(resultset[ind]);
            data.push(entry);
        }
        series.push(
            {
                name: resultsetattr,
                data: data,
                color: stringToColorCode(colorkey)
            }
        )
    }
    return series
}

function formatDatetimeTooltip2(x, y) {
    y = y.toPrecision(5)
    return '<b>' + Highcharts.dateFormat('%a %e %b %H:%M', x) + ", "+y+' </b><br />';
}

function formatDatetimeTooltip() {
    return formatDatetimeTooltip2(this.x, this.y)
}

function setExtremes(resultData, graphcontainer) {
    var chart = $('#' + graphcontainer).highcharts();

    // Fix y-axis range for certain metrics
    // fps and frametime values are inverse of each other
    if (resultData['metric'] === 'fps') {
        chart.yAxis[0].setExtremes(5, 150, true);
    }
    else if (resultData['metric'] === 'frametime') {
        chart.yAxis[0].setExtremes(0.008, 0.2, true);
    }
}

function DrawScatterGraph(resultData, title, graphcontainer, colorkey) {
    var series = dataToSeries(resultData, colorkey, keyvalueToPtConfig);

    var options =  {
        chart: {
            type: 'scatter',
            zoomType: 'xy',
            renderTo: graphcontainer,
            width: $(graphcontainer).width(),
            height: $(graphcontainer).height()

        },
        series: series,
        legend: {enabled: false},
        title: {text: title},
        xAxis:{type: 'datetime'},
        yAxis:{
            title: { enabled: false }
        },
        tooltip: {
            formatter: formatDatetimeTooltip
        },
        plotOptions: {
            series: {
                turboThreshold: 0,
                cursor: 'pointer',
                point: {
                    events: {
                        click: function() {

                            // Make variables accessible from jQuery function.
                            pageX = this.pageX;
                            pageY = this.pageY
                            chart_x = this.x;
                            chart_y = this.y;
                            id = this.id;
                            changelist = this.changelist;
                            branch = this.branch;

                            $.getJSON('/executionjson/'+ this.id +'?metric=' + resultData['metric'], function(execution_json_string) {
                            hs.htmlExpand(null, {
                                pageOrigin: {
                                    x: pageX,
                                    y: pageY
                                },
                                maincontentText: formatDatetimeTooltip2(chart_x, chart_y) +
                                    '<br />Changelist: ' + changelist +
                                    '<br />Branch: ' + branch +
                                    '<br />Average: ' + execution_json_string["meta"]["average"] +
                                    '<br />Max: ' + execution_json_string["meta"]["max"] +
                                    '<br />Min: ' + execution_json_string["meta"]["min"] +
                                    '<br />Mode: ' + execution_json_string["meta"]["mode"] +
                                    '<br />Range: ' + execution_json_string["meta"]["range"] +

                                    '<br /><a href="/execution/' + id +
                                    '?metric=' + resultData['metric'] +
                                    //Autopilot fps for TESTLAB-TA-REC for Changelist 100
                                    '&title=' + resultData['bench'] + ' ' + resultData['metric'] + ' on ' + resultData['machinename'] + ' for Changelist ' + changelist +
                                    '">View this execution</a>',
                                width: 200
                            });
                          })
                        }
                    }
                },
                marker: {
                    lineWidth: 1
                }
            }
        }
    };

    $('#' + graphcontainer).highcharts(options);
    setExtremes(resultData, graphcontainer);
}

function DrawThumbnailGraph(resultData, title, graphcontainer, colorkey) {
    var series = dataToSeries(resultData, colorkey, keyvalueToPtConfig);

    var options =  {
        chart: {
            type: 'line',
            zoomType: 'xy',
            renderTo: graphcontainer,
            width: $(graphcontainer).width(),
            height: $(graphcontainer).height()

        },
        title: {text: title, useHTML: true},
        series: series,
        legend: {enabled: false},
        xAxis: {
            title: {enabled: false},
            labels: {enabled: false},
            type: 'datetime'
        },
        yAxis: {
            title: {enabled: false},
            labels: {enabled: false}
        },
        tooltip: {
            formatter: formatDatetimeTooltip
        },
        plotOptions: {
            series: {
                marker: {
                    symbol: 'circle',
                    radius: 3
                }
            }
        }
    };

    $('#' + graphcontainer).highcharts(options);
    setExtremes(resultData, graphcontainer);

}


function DrawExecutionGraph(resultData, title, graphcontainer, colorkey) {
    var series = dataToSeries(resultData, colorkey, keyvalueToPair);

    var seriesStart = series[0].data[0][0];

    var options =  {
        chart: {
            type: 'line',
            zoomType: 'xy',
            renderTo: graphcontainer,
            width: $(graphcontainer).width(),
            height: $(graphcontainer).height()

        },
        title: {text: title},
        series: series,
        legend: {enabled: false},
        xAxis: {
            labels: {rotation: 25},
            type: 'datetime'
        },
        yAxis: {
            title: {enabled: false}
        },
        tooltip: {
            formatter: function () {
                return (this.x - seriesStart) + '<br />' + this.y;
            }
        },
        plotOptions: {
            series: {
                marker: {
                    enabled: false
                }
            }
        }
    };

    $('#' + graphcontainer).highcharts(options)
}
