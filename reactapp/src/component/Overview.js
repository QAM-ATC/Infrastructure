import React from 'react';
import Valuegraph from './ValueGraph';
import { makeStyles } from "@material-ui/core/styles";
import Paper from "@material-ui/core/Paper";
import Grid from "@material-ui/core/Grid";
import { green } from '@material-ui/core/colors';
import PortfolioSetting from './PortfolioSetting';
import Ratios from './Ratios';
import HeatMap from './HeatMap';
import UpdateDataButton  from './UpdateDataButton.js';


const useStyles = makeStyles(theme => ({
  root: {
    height: "100vh"
  },
  grid: {
    height: "100vh",
    background: 'green',
  },
  paperLeft: {
    height: "90%"
  },
  paperMain: {
    height: "90%"
  },
  paperRight: {},
  paper: {
    padding: theme.spacing(1),
    textAlign: "center",
    //color: theme.palette.text.primary,
    // background: theme.palette.grey
  }
}));

export default function FullWidthGrid() {
  const classes = useStyles();
  return (
    <div className={classes.root}>
      <Grid container spacing={1} className={classes.grid} justifyContent="space-evenly">
        <Grid item container xs={12} spacing={1}>
          <Grid item xs={8}>

          <Valuegraph/>
          </Grid>
          <Grid item container justifyContent="flex-start" direction="column" xs={4} spacing={2}>


          <Grid item xs={6}>
          <PortfolioSetting/>
          </Grid>

          <Grid item xs={5}>
          </Grid>
        
        </Grid>
        </Grid>
      </Grid>
    </div>
  );

  
}

