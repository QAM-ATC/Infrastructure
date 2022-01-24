import CanvasJSReact from '../lib/canvasjs.stock.react';
import React, {Component} from "react";
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import {connect} from 'react-redux';

var CanvasJS = CanvasJSReact.CanvasJS;
var CanvasJSStockChart = CanvasJSReact.CanvasJSStockChart;



class ValueGraph extends Component {
  render() {

    //const dummyData=[[1,728265600000],[1.0073787772,728524800000]];
    const dummyData=this.props.timeSeries;
    console.log("value graph")
    console.log(typeof(dummyData))
    let newDummy=dummyData.map(oneData => {
      let obj = {};
      obj['x'] = new Date(oneData[1]);
      obj['y'] = oneData[0]
      return obj;
    })
    const options = {
      title: {
          text: "Normalized portfolio value"
      },
      charts: [{
          data: [{
            type: "line",
            dataPoints: newDummy
         }]
      }],
    };
    const containerProps = {
      width: "90%",
      height: "80",
      margin: "auto",
    };

    if (this.props.timeSeries.length==0)
  return (<h1 >please change the setting and press the button</h1>);
    return (
      <div>
      <CanvasJSStockChart
        options={options}
        containerProps = {containerProps}
        onRef={ref => this.stockChart = ref}
      />
      
    </div>
    );

  }
}

const mapStateToProps=state=>
{
   console
    return {
      timeSeries: state.value.timeSeries 
    }
};
//If you want to access the Redux store data in any component you need to use 
// connect and make use of mapStateToProps to connect the store values to your props.

export default connect(mapStateToProps)(ValueGraph)


/*

<Stack spacing={2} direction="row">
     
      <Button variant="contained">Contained</Button>
      <Button variant="outlined">Outlined</Button>
    </Stack>
    );


[
	      { x: new Date("2018-01-01"), y: 71 },
	      { x: new Date("2018-02-01"), y: 55 },
	      { x: new Date("2018-03-01"), y: 50 },
	      { x: new Date("2018-04-01"), y: 65 },
	      { x: new Date("2018-05-01"), y: 95 },
	      { x: new Date("2018-06-01"), y: 68 },
	      { x: new Date("2018-07-01"), y: 28 },
	      { x: new Date("2018-08-01"), y: 34 },
	      { x: new Date("2018-09-01"), y: 14 },
	      { x: new Date("2018-10-01"), y: 71 },
	      { x: new Date("2018-12-01"), y: 50 },
	      { x: new Date("2019-01-01"), y: 34 },
	      { x: new Date("2019-02-01"), y: 50 },
	      { x: new Date("2019-03-01"), y: 50 },
	      { x: new Date("2019-04-01"), y: 95 },
	      { x: new Date("2019-05-01"), y: 68 },
	      { x: new Date("2019-06-01"), y: 28 },
	      { x: new Date("2019-07-01"), y: 34 },
	      { x: new Date("2019-08-01"), y: 65 },
	      { x: new Date("2019-09-01"), y: 55 },
	      { x: new Date("2019-10-01"), y: 71 },
	      { x: new Date("2019-11-01"), y: 55 },
	      { x: new Date("2019-12-01"), y: 50 }
	  ]

*/
