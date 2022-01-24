
import React  from "react";
import {Tabs,Tab,AppBar} from "@material-ui/core";
import Header from "./component/Header";
import {BrowserRouter,Route,Switch,Link} from "react-router-dom";
import Correlation from "./component/Correlation"
import Overview from "./component/Overview"
import Frontier from "./component/Frontier"
import Return_distribution from "./component/Return_distribution";
import "react-loader-spinner/dist/loader/css/react-spinner-loader.css";

import store from './redux/store'
import { Provider } from "react-redux";






// action creater





export default function App() {
    const routes =["/overview","/correlation","/return_distribution","/efficient_frontier"];
  return (
    <Provider store={store}>
    <div className="App">
        <Header/>
          <BrowserRouter>
          
      <div>
        <Route
          path="/"
          render={(history) => (
            <AppBar position="static">
              <Tabs centered
                value={
                  history.location.pathname !== "/"
                    ? history.location.pathname
                    : false
                }
              >

<Tab
                  value={routes[0]}
                  label="overview"
                  component={Link}
                  to={routes[0]}
                />
                <Tab
                  value={routes[1]}
                  label="correlation"
                  component={Link}
                  to={routes[1]}
                />

<Tab
                  value={routes[2]}
                  label="return_distribution"
                  component={Link}
                  to={routes[2]}
                />


<Tab
                  value={routes[3]}
                  label="efficient_frontier"
                  component={Link}
                  to={routes[3]}
                />

              </Tabs>
            </AppBar>
          )}
        />

<Switch>
          <Route path="/overview" component={Overview} />
          <Route path="/correlation" component={Correlation} />
          <Route path="/return_distribution" component={Return_distribution} />
          <Route path="/efficient_frontier" component={Frontier} />
        </Switch>
        </div>
      </BrowserRouter>
    </div>
    </Provider>
  );
}


