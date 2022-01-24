import React from 'react';
import Grid from '@material-ui/core/Grid';
import Paper from '@material-ui/core/Paper';
import Typography from '@material-ui/core/Typography';
export default function()
{
    return (

        <Paper sx={{ p: 2, margin: 'auto', maxWidth: 700, minWidth: 600,flexGrow: 2 }}>
        <Grid
          container
          direction="column"
          justifyContent="center"
          alignItems="center"
        >

<Typography gutterBottom variant="h5" component="div">
                number1 
              </Typography>
              <Typography gutterBottom variant="h5" component="div">
                number12
              </Typography>

        </Grid>
        </Paper>
    );
}