import { ResponsiveHeatMap } from '@nivo/heatmap'
import {changeCorrelation} from '../redux/value/actions';
import {connect} from 'react-redux';

 
// make sure parent container have a defined height when using
// responsive component, otherwise height will be 0 and
// no chart will be rendered.
// website examples showcase many properties,
// you'll often use just a few of them.

// https://nivo.rocks/heatmap/
// https://learn.co/lessons/map-state-to-props-readme

//props.correlation
import React from 'react';

function  HeatMap(props)
{


    //const data=props.correlation
  //   const data= [{
  //     "id": "Japan",
  //     "data": [{
  //         "x": "Train",
  //         "y": -0.3
  //       },
  //       {
  //         "x": "Bus",
  //         "y": 0.8
  //       }
  //     ]
  //   },
  //   {
  //     "id": "China",
  //     "data": [{
  //         "x": "Train",
  //         "y": -0.4
  //       },
  //       {
  //         "x": "Bus",
  //         "y": 0.9
  //       }
  //     ]
  //   }
  // ]
  if (props.correlation.length==0)
  return (<h1 >please change the setting and press the button</h1>);
    return (
       
        <ResponsiveHeatMap
        data={props.correlation}
        margin={{ top: 60, right: 90, bottom: 60, left: 90 }}
        valueFormat=">+.2r"
        axisTop={{
            tickSize: 5,
            tickPadding: 5,
            tickRotation: -90,
            legend: '',
            legendOffset: 46
        }}
        axisRight={{
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
            //legend: 'STOCKS',
            legendPosition: 'middle',
            legendOffset: 70
        }}
        axisLeft={{
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
            //legend: 'STOCKS',
            legendPosition: 'middle',
            legendOffset: -72
        }}
        colors={{
            type: 'diverging',
            scheme: 'red_yellow_blue',
            divergeAt: 0.5,
            minValue: -1,
            maxValue: 1
        }}
        emptyColor="#555555"
        legends={[
            {
                anchor: 'bottom',
                translateX: 0,
                translateY: 30,
                length: 400,
                thickness: 8,
                direction: 'row',
                tickPosition: 'after',
                tickSize: 3,
                tickSpacing: 4,
                tickOverlap: false,
                tickFormat: '>+.2r',
                title: 'Value →',
                titleAlign: 'start',
                titleOffset: 4
            }
        ]}
    />
    );
}



const mapStateToProps=state=>
{
   console
    return {
      correlation: state.value.correlation   
    }
};
//If you want to access the Redux store data in any component you need to use 
// connect and make use of mapStateToProps to connect the store values to your props.

export default connect(mapStateToProps)(HeatMap)






// https://www.basefactor.com/react-how-to-display-a-loading-indicator-on-fetch-calls