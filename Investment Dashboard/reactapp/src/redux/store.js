
import { combineReducers ,createStore} from "redux";

const initialSettingState={
    frequency: '',
    chosenStocks : [],
    period:'',

}

// REDUCER
const Settingreducer=(state=initialSettingState,action)=>{




    
    switch(action.type)
    {
      case "CHANGEFREQUENCY":
        return {...state,frequency:action.payload};
      case "CHANGESTOCKS":
        return {...state,chosenStocks:action.payload}
      case "CHANGEPERIOD":
          return {...state,period:action.payload}
  
      default:
        return state;
  
  
    }
  }


  const initialValueState={
    timeSeries:[],
    correlation:[],
    loading: false
}

// REDUCER
const Valuereducer=(state=initialValueState,action)=>{

  console.log("hi in value reducer")
  console.log(action.type)
    switch(action.type)
    {
      case "CHANGETIMESERIES":
        return {...state,timeSeries:action.payload};
      case "CHANGECORRELATION":
        console.log("change correlation in value reducer");
        return {...state,correlation:action.payload}
  
      default:
        return state;
  
  
    }
  }


  const rootReducer= combineReducers(
      {
          setting:Settingreducer,
          value:Valuereducer
      }
  )

// reducer create and change the store 

export default createStore(rootReducer)