am4core.ready(function() {

    // Themes begin
    am4core.useTheme(am4themes_animated);
    // Themes end
    
    dom_chart = am4core.create("chartdiv2", am4charts.XYChart);
    dom_chart.hiddenState.properties.opacity = 0; // this makes initial fade in effect
    dom_chart.responsive.enabled = true;
    dom_chart.exporting.menu = new am4core.ExportMenu();
    
    // dom_chart.data = {};
     
     dom_chart.padding(0, 20, 20, 0);
     
     var categoryAxis = dom_chart.yAxes.push(new am4charts.CategoryAxis());
     categoryAxis.renderer.grid.template.location = 0;
     categoryAxis.dataFields.category = "title";
     categoryAxis.renderer.minGridDistance = 60;
     categoryAxis.renderer.inversed = true;
     categoryAxis.renderer.grid.template.disabled = true;
     
     var valueAxis = dom_chart.xAxes.push(new am4charts.ValueAxis());
     valueAxis.min = 0;
     valueAxis.max = 100;
     valueAxis.extraMax = 0.1; 
     valueAxis.strictMinMax = true;
     //valueAxis.rangeChangeEasing = am4core.ease.linear;
     //valueAxis.rangeChangeDuration = 1500;
     
     var series = dom_chart.series.push(new am4charts.ColumnSeries());
     series.dataFields.categoryY = "title";
     series.dataFields.valueX = "value";
     series.tooltipText = "{value.value}"
     series.columns.template.strokeOpacity = 0;
     series.columns.template.column.cornerRadiusTopRight = 10;
     series.columns.template.column.cornerRadiusBottomRight = 10;
     series.interpolationDuration = 1500;
     
     //series.interpolationEasing = am4core.ease.linear;
     var labelBullet = series.bullets.push(new am4charts.LabelBullet());
     //labelBullet.label.verticalCenter = "center";
     labelBullet.label.dx = -20;
     labelBullet.label.text = "{values.valueX.value}%";
     labelBullet.label.fill = am4core.color("white");
     labelBullet.label.fontWeight = "bold";
     
     var label = categoryAxis.renderer.labels.template;
     label.wrap = true;
     label.maxWidth = 180;
     label.align = "left";
     categoryAxis.renderer.minGridDistance = 20;
     label.fontSize = 12;

     
     dom_chart.zoomOutButton.disabled = true;
     
     // as by default columns of the same series are of the same color, we add adapter which takes colors from chart.colors color set
     series.columns.template.adapter.add("fill", function (fill, target) {
      return dom_chart.colors.getIndex(target.dataItem.index);
     });
     



     var indicator;
     function showIndicator() {
        if (indicator) {
            indicator.show();
        }
        else {
            indicator = dom_chart.tooltipContainer.createChild(am4core.Container);
            indicator.background.fill = am4core.color("#fff");
            indicator.background.fillOpacity = 0.8;
            indicator.width = am4core.percent(100);
            indicator.height = am4core.percent(100);

            var indicatorLabel = indicator.createChild(am4core.Label);
            indicatorLabel.text = "Select a Security Dimension first";
            indicatorLabel.align = "center";
            indicatorLabel.valign = "middle";
            indicatorLabel.fontSize = 20;
        }
     }

     function hideIndicator() {
        indicator.hide();
      }


    //  dom_chart.addLabel(0, '50%', 'Select a Security Dimension first', 'center');
      dom_chart.events.on("beforedatavalidated", function() {
        if (jQuery.isEmptyObject(dom_chart.data)) 
            showIndicator();
        else
            hideIndicator();
      });
    //  categoryAxis.sortBySeries = series;
     
     }); // end am4core.ready()