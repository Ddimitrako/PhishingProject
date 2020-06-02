am4core.ready(function() {

    // Themes begin
    am4core.useTheme(am4themes_animated);
    // Themes end
    
    var chart = am4core.create("chartdiv2", am4charts.XYChart);
    chart.hiddenState.properties.opacity = 0; // this makes initial fade in effect
    








    chart.data = [{
      "domain": "Application Software Security",
      "score": 80
     }, {
      "domain": "Data Security and Privacy",
      "score": 50
     }, {
      "domain": "Hardware Assets Management",
      "score": 0
     }, {
      "domain": "Hardware Configuration Management",
      "score": 40
     }, {
      "domain": "Information Resources Management",
      "score": 30
     }, {
      "domain": "Network Configuration Management",
      "score": 60
     }, {
      "domain": "Network Infrastructure Management",
      "score": 50
     }, {
      "domain": "Software Assets Management",
      "score": 90
     }];
     
    //  chart.padding(40, 40, 40, 40);
     
     var categoryAxis = chart.yAxes.push(new am4charts.CategoryAxis());
     categoryAxis.renderer.grid.template.location = 0;
     categoryAxis.dataFields.category = "domain";
     categoryAxis.renderer.minGridDistance = 60;
     categoryAxis.renderer.inversed = true;
     categoryAxis.renderer.grid.template.disabled = true;
     
     var valueAxis = chart.xAxes.push(new am4charts.ValueAxis());
     valueAxis.min = 0;
     valueAxis.extraMax = 0.1;
     //valueAxis.rangeChangeEasing = am4core.ease.linear;
     //valueAxis.rangeChangeDuration = 1500;
     
     var series = chart.series.push(new am4charts.ColumnSeries());
     series.dataFields.categoryY = "domain";
     series.dataFields.valueX = "score";
     series.tooltipText = "{value.value}"
     series.columns.template.strokeOpacity = 0;
     series.columns.template.column.cornerRadiusTopRight = 10;
     series.columns.template.column.cornerRadiusBottomRight = 10;
     //series.interpolationDuration = 1500;
     //series.interpolationEasing = am4core.ease.linear;
     var labelBullet = series.bullets.push(new am4charts.LabelBullet());
     //labelBullet.label.verticalCenter = "center";
     labelBullet.label.dx = 20;
     labelBullet.label.text = "{values.valueX.workingValue.formatNumber('#.')}";
     
     var label = categoryAxis.renderer.labels.template;
    label.wrap = true;
    label.maxWidth = 200;
    label.align = "right";
    categoryAxis.renderer.minGridDistance = 20;

     
     chart.zoomOutButton.disabled = true;
     
     // as by default columns of the same series are of the same color, we add adapter which takes colors from chart.colors color set
     series.columns.template.adapter.add("fill", function (fill, target) {
      return chart.colors.getIndex(target.dataItem.index);
     });
     
     
    //  categoryAxis.sortBySeries = series;
     
     }); // end am4core.ready()