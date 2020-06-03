am4core.ready(function() {

    // // Themes begin
    // am4core.useTheme(am4themes_animated);
    // // Themes end
    
    // dim_chart = am4core.create("chartdiv1", am4charts.XYChart);
    // dim_chart.hiddenState.properties.opacity = 0; // this makes initial fade in effect
    
    // dim_chart.data = graph_data['dimensions'];
    
    
    // var categoryAxis = dim_chart.xAxes.push(new am4charts.CategoryAxis());
    // categoryAxis.renderer.grid.template.location = 0;
    // categoryAxis.dataFields.category = "title";
    // categoryAxis.renderer.minGridDistance = 40;
    
    // var valueAxis = dim_chart.yAxes.push(new am4charts.ValueAxis());
    
    // var series = dim_chart.series.push(new am4charts.CurvedColumnSeries());
    // series.dataFields.categoryX = "title";
    // series.dataFields.valueY = "value";
    // series.tooltipText = "{valueY.value}"
    // series.columns.template.strokeOpacity = 0;
    // series.columns.template.tension = 1;
    
    // series.columns.template.fillOpacity = 0.75;
    
    // var hoverState = series.columns.template.states.create("hover");
    // hoverState.properties.fillOpacity = 1;
    // hoverState.properties.tension = 0.8;
    
    // dim_chart.cursor = new am4charts.XYCursor();
    
    // // Add distinctive colors for each column using adapter
    // series.columns.template.adapter.add("fill", function(fill, target) {
    //   return dim_chart.colors.getIndex(target.dataItem.index);
    // });
    
    // // dim_chart.scrollbarX = new am4core.Scrollbar();
    // // dim_chart.scrollbarY = new am4core.Scrollbar();

    // series.columns.template.togglable = true;
    // var hs = series.columns.template.states.create("active");
    // hs.properties.fill = am4core.color("#E94F37");

    // series.columns.template.events.on("hit", function(ev) {
    //   console.log("clicked on ", ev.target.dataItem.categories.categoryX);
    //   console.log(ev.target.dataItem);
    //   // ev.target.dataItem.column.fill = am4core.color("#E94F37");
    //   // ev.target.column.fill = am4core.color("#E94F37");
    //   var seriesColumn = ev.target.dataItem.component.columns.template;
    //   seriesColumn.isActive = true;

    //  }, this);



    am4core.useTheme(am4themes_animated);
    dim_chart = am4core.create("chartdiv1", am4charts.XYChart);
    dim_chart.hiddenState.properties.opacity = 0; // this creates initial fade-in
    dim_chart.data = graph_data['dimensions'];

    var categoryAxis = dim_chart.xAxes.push(new am4charts.CategoryAxis());
    categoryAxis.renderer.grid.template.location = 0;
    categoryAxis.dataFields.category = "title";
    categoryAxis.renderer.minGridDistance = 40;

    var valueAxis = dim_chart.yAxes.push(new am4charts.ValueAxis());
    // valueAxis.min = 0;
    // valueAxis.max = 100;
    // valueAxis.strictMinMax = true;
    // valueAxis.renderer.minGridDistance = 40;

    var series = dim_chart.series.push(new am4charts.ColumnSeries());
    series.dataFields.categoryX = "title";
    series.dataFields.valueY = "value";
    series.columns.template.tooltipText = "{valueY.value}";
    series.columns.template.tooltipY = 0;
    series.columns.template.strokeOpacity = 0;
    series.columns.template.tension = 1;
    series.columns.template.fillOpacity = 0.75;
    

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
      series.columns.values
        .filter(c => c !== ev.target)
        .forEach(c => c.isActive = false);
      ev.target.isActive = !ev.target.isActive;

      $.each(graph_data['dimensions'], function( idx, dim ) {
        if(dim['title'] === ev.target.dataItem.categories.categoryX){
          dom_chart.data = dim['domains'];
          dom_chart.invalidateData();
            // dom_chart.animateAgain();
        }
      });
    });
    
    }); // end am4core.ready()