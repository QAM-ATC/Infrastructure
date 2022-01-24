import * as React from 'react';
import TextField from '@material-ui/core/TextField';
import Autocomplete from '@material-ui/lab/Autocomplete';
import CircularProgress from '@material-ui/core/CircularProgress';
import { makeStyles } from '@material-ui/core/styles';
import axios from 'axios'
import {changeStocks} from '../redux/setting/actions';
import { connect } from 'react-redux';

const useStyles = makeStyles((theme) => ({
  root: {
    width: 200,
    '& > * + *': {
      marginTop: theme.spacing(3),
    },
  },
}));

  function Asynchronous(props) {
  const [open, setOpen] = React.useState(false);
  const [options, setOptions] = React.useState(props.chosenStocks);   // the options are different from stock, they are from api 
  const loading = open && options.length === 0;
  const classes=useStyles();

  React.useEffect(() => {
    let active = true;

    if (!loading) {
      return undefined;
    }
    
    
    (async () => {
      //await sleep(1e3); // For demo purposes.
      const response=await axios.get('http://127.0.0.1:5000/stocks');

      if (active) {
        console.log("done")
        setOptions([...response.data]);
      }
    })();

    return () => {
      active = false;
    };
  }, [loading]);

  React.useEffect(() => {
    if (!open) {
      setOptions([]);
    }
  }, [open]);
  return (
    <div className={classes.root}>
    <Autocomplete 
    multiple 
    id="tags-outlined"
      //sx={{ width: 300 }}
      open={open}
      onOpen={() => {
        setOpen(true);
      }}
      onClose={() => {
        setOpen(false);
      }}
      onChange={(event,value)=>{
        console.log("new value is",value)
        props.changeStocks(value)
        // the value is simply the list of selected values
        //https://stackoverflow.com/questions/58666189/getting-the-value-in-the-react-material-ui-autocomplete

      }}
      //isOptionEqualToValue={(option, value) => option.title === value.title}
      //getOptionLabel={(option) => option.title}
      //getOptionLabel= {options}
      options={options}
      loading={loading}
      filterSelectedOptions
      defaultValue={ props.chosenStocks}
      
      renderInput={(params) => (
        <TextField
          {...params}
          variant="outlined"
          label="Stocks"
          InputProps={{
            ...params.InputProps,
            endAdornment: (
              <React.Fragment>
                {loading ? <CircularProgress color="inherit" size={20} /> : null}
                {params.InputProps.endAdornment}
              </React.Fragment>
            ),
          }}
        />
      )}
    />
    </div>
  );
}


const mapStateToProps=state=>
{
    return {
        chosenStocks: state.setting.chosenStocks
        
    }
};
//chosenStocks: state.chosenStocks

const mapDispatchToprops= dispatch=>{
    return {
        //changeFrequency: (newFrequency)=>  dispatch(changeFrequency(newFrequency)) 
        changeStocks: (stocks)=>  dispatch(changeStocks(stocks))

        //changeFrequency: newFrequency=>  console.log(newFrequency)
        //changeFrequency: ()=>  dispatch()
        
        }
    };

export default connect(mapStateToProps,mapDispatchToprops)(Asynchronous)
/*
const data=["hi","123"];
// Top films as rated by IMDb users. http://www.imdb.com/chart/top
const topFilms = [
  { title: 'The Shawshank Redemption', year: 1994 },
  { title: 'The Godfather', year: 1972 },
  { title: 'The Godfather: Part II', year: 1974 },
  { title: 'The Dark Knight', year: 2008 },
  { title: '12 Angry Men', year: 1957 },
  { title: "Schindler's List", year: 1993 },
  { title: 'Pulp Fiction', year: 1994 },
  {
    title: 'The Lord of the Rings: The Return of the King',
    year: 2003,
  },
  { title: 'The Good, the Bad and the Ugly', year: 1966 },
  { title: 'Fight Club', year: 1999 },
  {
    title: 'The Lord of the Rings: The Fellowship of the Ring',
    year: 2001,
  },
  {
    title: 'Star Wars: Episode V - The Empire Strikes Back',
    year: 1980,
  },
  { title: 'Forrest Gump', year: 1994 },
  { title: 'Inception', year: 2010 },
  {
    title: 'The Lord of the Rings: The Two Towers',
    year: 2002,
  },
  { title: "One Flew Over the Cuckoo's Nest", year: 1975 },
  { title: 'Goodfellas', year: 1990 },
  { title: 'The Matrix', year: 1999 },
  { title: 'Seven Samurai', year: 1954 },
  {
    title: 'Star Wars: Episode IV - A New Hope',
    year: 1977,
  },
  { title: 'City of God', year: 2002 },
  { title: 'Se7en', year: 1995 },
  { title: 'The Silence of the Lambs', year: 1991 },
  { title: "It's a Wonderful Life", year: 1946 },
  { title: 'Life Is Beautiful', year: 1997 },
  { title: 'The Usual Suspects', year: 1995 },
  { title: 'Léon: The Professional', year: 1994 },
  { title: 'Spirited Away', year: 2001 },
  { title: 'Saving Private Ryan', year: 1998 },
  { title: 'Once Upon a Time in the West', year: 1968 },
  { title: 'American History X', year: 1998 },
  { title: 'Interstellar', year: 2014 },
];


*/



// https://codesandbox.io/s/ihc26?file=/demo.js

//https://codesandbox.io/s/asynchronous-material-demo-forked-513li?file=/demo.js:0-3463