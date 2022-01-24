

export const changeCorrelation= (newCorrelation)=>
{
  return {
    type: 'CHANGECORRELATION',
    payload: newCorrelation
  }
}


export const changeTimeSeries=(newTimeSeries)=>
{
  return {
    type: 'CHANGETIMESERIES',
    payload: newTimeSeries
  }
}