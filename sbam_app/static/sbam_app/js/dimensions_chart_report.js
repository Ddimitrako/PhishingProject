am4core.ready(function() {

    am4core.useTheme(am4themes_animated);
    dim_chart = am4core.create("chartdiv1", am4charts.XYChart);
    dim_chart.hiddenState.properties.opacity = 0; // this creates initial fade-in
    dim_chart.responsive.enabled = true;
    dim_chart.exporting.menu = new am4core.ExportMenu();
    // dim_chart.data = graph_data['dimensions'];

    var categoryAxis = dim_chart.xAxes.push(new am4charts.CategoryAxis());
    categoryAxis.renderer.grid.template.location = 0;
    categoryAxis.dataFields.category = "title";
    categoryAxis.renderer.minGridDistance = 30;
    
    var label = categoryAxis.renderer.labels.template;
    label.wrap = true;
    label.fontSize = 12;
    label.fontWeight = 'bold';
    // label.truncate = true;
    label.maxWidth = 95;
    label.adapter.add("fill", function(fill, target) {
      if(target.dataItem.dataContext){
        //console.log(target.dataItem.dataContext.level);
        if (target.dataItem.dataContext.level==0)
          return am4core.color("#217c07");
        else
          return am4core.color("#9b4907");
      }
    });

    categoryAxis.events.on("sizechanged", function(ev) {
        var axis = ev.target;
        var cellWidth = axis.pixelWidth / (axis.endIndex - axis.startIndex);
        // label.maxWidth = cellWidth;
        if (cellWidth < label.maxWidth) {
          label.rotation = -30;
          label.horizontalCenter = "middle";
        }
        else {
          label.rotation = 0;
          label.horizontalCenter = "middle";
        }
      });

    var valueAxis = dim_chart.yAxes.push(new am4charts.ValueAxis());
    valueAxis.min = 0;
    valueAxis.max = 100;
    valueAxis.strictMinMax = true;
    // valueAxis.renderer.minGridDistance = 40;

    var series = dim_chart.series.push(new am4charts.ColumnSeries());
    series.dataFields.categoryX = "title";
    series.dataFields.valueY = "value";
    series.columns.template.tooltipText = "{categoryX}:{valueY.value}%";
    series.columns.template.tooltipY = 0;
    series.columns.template.strokeOpacity = 0;
    series.columns.template.tension = 1;
    series.columns.template.fillOpacity = 0.75;
    series.interpolationDuration = 1500;
    series.columns.template.cursorOverStyle = am4core.MouseCursorStyle.pointer;

    

    var hoverState = series.columns.template.states.create("hover");
    hoverState.properties.fillOpacity = 0.9;
    hoverState.properties.tension = 0.8;

    series.columns.template.adapter.add("fill", function(fill, target) {
      return dim_chart.colors.getIndex(target.dataItem.index);
    });

    var activeState = series.columns.template.states.create("active");
    activeState.properties.fill = am4core.color('#a02e2e');
    activeState.properties.fillOpacity = 1;
    activeState.properties.strokeOpacity = 1;
    activeState.properties.stroke = am4core.color("orange");

    series.columns.template.events.on("hit", function(ev) {
      series.columns.values.forEach(c => c.isActive = false);
      ev.target.isActive = !ev.target.isActive;
      console.log(ev.target.dataItem);
      $.each(graph_data['dimensions'], function( idx, dim ) {
        if(dim['title'] === ev.target.dataItem.categories.categoryX){
          dom_chart.data = dim['domains'];
          dom_chart.invalidateData();
          dom_chart.reinit();
        }
      });
    });
    
    }); // end am4core.ready()