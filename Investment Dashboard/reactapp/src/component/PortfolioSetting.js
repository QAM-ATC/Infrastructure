import React from 'react';
import { makeStyles ,useTheme} from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Paper from '@material-ui/core/Paper';
import Typography from '@material-ui/core/Typography';
import ButtonBase from '@material-ui/core/ButtonBase';
import Select from '@material-ui/core/Select';
import Input from '@material-ui/core/Input';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormHelperText from '@material-ui/core/FormHelperText';
import FormControl from '@material-ui/core/FormControl';
import Button from '@material-ui/core/Button';
import {changeFrequency,changeStocks,changePeriod} from '../redux/setting/actions';
import Asynchronous from './StocksSelection';

import Chip from '@material-ui/core/Chip';
import { connect } from 'react-redux';
import UpdateDataButton  from './UpdateDataButton.js';



const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;

const MenuProps = {
    PaperProps: {
      style: {
        maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
        width: 250,
      },
    },
  };
  
  const names = [
    'SEA',
    'APPL',
    'DBS',
    'Meta',
  ];




  // value are set according to yfiance api so that, we can use the api directlyhttps://pypi.org/project/yfinance/
  const HistoricalPeriods=[
    '1d','5d','1mo','3mo','6mo','1y','2y','5y','10y','max'
  ]
  const HistoricalPeriodsNames=['One day','Five days','One month','Three Months','Six Months','One year','Two years','Five years','Ten years','Max period avaliable']
  let PeriodOptionsList=[]
  HistoricalPeriods.forEach(
    (item,index)=>{
      PeriodOptionsList.push(  <MenuItem value={item}>{HistoricalPeriodsNames[index]}</MenuItem>)
    }

  )

  const intervals=['1d','5d','1wk','1mo','3mo']  // frequency
  const intervalsName=['One day','Five days','One week','One month','Three Months']
  let intervalsOptionsList=[]
  intervals.forEach(
    (item,index)=>{
      intervalsOptionsList.push(<MenuItem value={item}>{intervalsName[index]}</MenuItem>)
    }
  )


const useStyles = makeStyles((theme) => ({
    root: {
      flexGrow: 1,
    },
    paper: {
      padding: theme.spacing(2),
      margin: 'auto',
      maxWidth: 500,
      minWidth: 200,
    },
    formControl: {
        margin: theme.spacing(1),
        minWidth: 200,
      },
      selectEmpty: {
        marginTop: theme.spacing(2),
      },
      chips: {
        display: 'flex',
        flexWrap: 'wrap',
      },
      chip: {
        margin: 2,
      },
  }));

  function getStyles(name, personName, theme) {
    return {
      fontWeight:
        personName.indexOf(name) === -1
          ? theme.typography.fontWeightRegular
          : theme.typography.fontWeightMedium,
    };
  }

  function PortfolioSetting(props) {

    const classes = useStyles();
  
    const handleChangePeriod = (event) => {
      props.changePeriod(event.target.value);
    };
   
    // const [frequency, setFrequency] = React.useState(props.frequency);
    const handleChangeFrequency = (event) => {

        props.changeFrequency(event.target.value);
        //console.log(event.target.value);

      };

    const theme = useTheme();
  
  return (
    <Paper sx={{ p: 2, margin: 'auto', maxWidth: 700, flexGrow: 1 }}>
            <Grid
  container
  direction="column"
  justifyContent="center"
  alignItems="center"
>

              <Typography gutterBottom variant="h4" component="div">
                Custome portfolio
              </Typography>


              <FormControl variant="outlined" className={classes.formControl}>
        <InputLabel id="demo-simple-select-outlined-label"> Historical period </InputLabel>
        <Select
          labelId="demo-simple-select-outlined-label"
          id="demo-simple-select-outlined"
          value={props.period}
          onChange={handleChangePeriod}
          label="Historical Period"
        >
          {PeriodOptionsList}
        </Select>
      </FormControl>




      <FormControl variant="outlined" className={classes.formControl}>
        <InputLabel id="demo-simple-select-outlined-label">  Interval </InputLabel>
        <Select
          labelId="demo-simple-select-outlined-label"
          id="demo-simple-select-outlined"
          value={props.frequency}
          onChange={handleChangeFrequency}
          label="frequency"
        >
          {intervalsOptionsList}
        </Select>
      </FormControl>

      <Asynchronous/>

      <UpdateDataButton/>



            </Grid>

    
          </Paper>
  );
};


const mapStateToProps=state=>
{
    return {
        frequency: state.setting.frequency,
        period: state.setting.period
        
    }
};
//chosenStocks: state.chosenStocks

const mapDispatchToprops= dispatch=>{
    return {
        changeFrequency: (newFrequency)=>  dispatch(changeFrequency(newFrequency)),
        changePeriod: (newPeriod)=>  dispatch(changePeriod(newPeriod)) 

        //changeFrequency: newFrequency=>  console.log(newFrequency)
        //changeFrequency: ()=>  dispatch()
        
        }
    };

export default connect(mapStateToProps,mapDispatchToprops)(PortfolioSetting)

// changeStocks: newStocks=> {dispatch(changeStocks(newStocks))}



/*
      <FormControl variant="outlined" className={classes.formControl}>
        <InputLabel id="demo-mutiple-chip-label">Stocks</InputLabel>
        <Select
          labelId="demo-mutiple-chip-label"
          id="demo-mutiple-chip"
          multiple
          value={personName}
          onChange={handleChangeStocks}
          input={<Input id="select-multiple-chip" />}
          renderValue={(selected) => (
            <div className={classes.chips}>
              {selected.map((value) => (
                <Chip key={value} label={value} className={classes.chip} />
              ))}
            </div>
          )}
          MenuProps={MenuProps}
        >
          {names.map((name) => (
            <MenuItem key={name} value={name} style={getStyles(name, personName, theme)}>
              {name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>


*/
