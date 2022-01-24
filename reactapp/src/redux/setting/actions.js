

export const changeFrequency= (newFrequency)=>
{
    console.log("i am the changeFrequency function")
  return {
    type: 'CHANGEFREQUENCY',
    payload: newFrequency
  }
}

export const changePeriod= (newperiod)=>
{
  return {
    type: 'CHANGEPERIOD',
    payload: newperiod
  }
}


export const changeStocks=(newStocks)=>
{
  return {
    type: 'CHANGESTOCKS',
    payload: newStocks
  }
}




