am4core.ready(function() {

    // Themes begin
    am4core.useTheme(am4themes_animated);
    // Themes end
    
    var chart = am4core.create("chartdiv1", am4charts.XYChart);
    chart.hiddenState.properties.opacity = 0; // this makes initial fade in effect
    
    chart.data = [{
        "dimension": "Assets",
        "value": 65
        }, {
        "dimension": "Continuity",
        "value": 45
        }, {
        "dimension": "Access and Trust",
        "value": 70
        }, {
        "dimension": "Operations",
        "value": 37
        }, {
        "dimension": "Defense",
        "value": 80
        }, {
        "dimension": "Security Governance",
        "value": 30
        }, {
        "dimension": "Attitude",
        "value": 50
        }, {
        "dimension": "Awareness",
        "value": 60
        }, {
        "dimension": "Behaviour",
        "value": 30
        }, {
        "dimension": "Competency",
        "value": 70
        }];
    
    
    var categoryAxis = chart.xAxes.push(new am4charts.CategoryAxis());
    categoryAxis.renderer.grid.template.location = 0;
    categoryAxis.dataFields.category = "dimension";
    categoryAxis.renderer.minGridDistance = 40;
    
    var valueAxis = chart.yAxes.push(new am4charts.ValueAxis());
    
    var series = chart.series.push(new am4charts.CurvedColumnSeries());
    series.dataFields.categoryX = "dimension";
    series.dataFields.valueY = "value";
    series.tooltipText = "{valueY.value}"
    series.columns.template.strokeOpacity = 0;
    series.columns.template.tension = 1;
    
    series.columns.template.fillOpacity = 0.75;
    
    var hoverState = series.columns.template.states.create("hover");
    hoverState.properties.fillOpacity = 1;
    hoverState.properties.tension = 0.8;
    
    chart.cursor = new am4charts.XYCursor();
    
    // Add distinctive colors for each column using adapter
    series.columns.template.adapter.add("fill", function(fill, target) {
      return chart.colors.getIndex(target.dataItem.index);
    });
    
    // chart.scrollbarX = new am4core.Scrollbar();
    // chart.scrollbarY = new am4core.Scrollbar();
    
    }); // end am4core.ready()