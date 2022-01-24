import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import { changeCorrelation,changeTimeSeries} from '../redux/value/actions';
import { connect } from 'react-redux';
import axios from 'axios'






const useStyles = makeStyles((theme) => ({
    root: {
      '& > *': {
        margin: theme.spacing(1),
      },
    },
  }));
  
function UpdateDataButton(props) {
    const classes = useStyles();
  
    return (
      <div className={classes.root}>
        <Button variant="contained" color="secondary"
        onClick = {() => {

        /*
    Begin by setting loading = true, and use the callback function
    of setState() to make the ajax request. Set loading = false after
    the request completes.
    // https://mocki.io/v1/972be843-6888-4359-aa83-d6f59cdef0b1

    
  */  if (props.frequency &&  props.period &&  props.chosenStocks.length>0)
  {
 let stocksStringList=props.chosenStocks.map(x=> "stocks="+x);
      // alert('http://127.0.0.1:5000/getCorrelation?'+stocksStringList.join('&'))

      axios.get('http://127.0.0.1:5000/getCorrelation?'+stocksStringList.join('&')+'&frequency='+props.frequency+'&period='+props.period).then(response=>
      {
        // response.data is the array of stocks 
        props.changeCorrelation(response.data)
      
      });

     //alert('http://127.0.0.1:5000/getGraphValue?'+stocksStringList.join('&')+'&frequency='+props.frequency)
      // get graph value  https://mocki.io/v1/45bb99e8-e418-4d2f-886e-02796c088ec3
       axios.get('http://127.0.0.1:5000/getGraphValue?'+stocksStringList.join('&')+'&frequency='+props.frequency+'&period='+props.period).then(response=>
      {
        props.changeTimeSeries(response.data);
      
           });
        }

      else 
      {
        alert("fill up all the settings")
      }
    
    }
      }
        >
          Apply Setting
        </Button>
      </div>
    );
  }



  const mapStateToProps=state=>
{
    return {
        correlation: state.value.correlation,
        timeSeries: state.value.timeSeries,
        frequency: state.setting.frequency,
        chosenStocks : state.setting.chosenStocks,
        period : state.setting.period


        
    }
};
//chosenStocks: state.chosenStocks

const mapDispatchToprops= dispatch=>{
    return {
        changeTimeSeries: (newTimeSeries)=>  dispatch(changeTimeSeries(newTimeSeries)),
        changeCorrelation :(newCorrelation)=> dispatch(changeCorrelation(newCorrelation))
        
        }
    };

export default connect(mapStateToProps,mapDispatchToprops)(UpdateDataButton)



/*


*/