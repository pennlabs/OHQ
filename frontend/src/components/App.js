import React from 'react';
import { BrowserRouter as Router, Route, Switch, Redirect} from 'react-router-dom';
import * as ROUTES from '../constants/routes';

import LandingPage from './LandingPage/LandingPage';
import Home from './Home/Home';
import Main from './Main/Main';
import Course from './Course/Course';
import Student from './Student/Student';

import { withAuthentication } from './Session';

const App = () => {
  return (
    <Router>
      <Switch>
        <Route exact path={ROUTES.LANDING} component={ LandingPage }/>
        <Route exact path={ROUTES.HOME} component={ Home }/>
        <Route exact path={ROUTES.CLASS} component={ Main }/>
        <Route exact path={ROUTES.COURSE} component={ Course }/>
        <Route exact path={ROUTES.STUDENT} component={ Student }/>
        <Redirect to="/" />
      </Switch>
    </Router>
  )
};

export default withAuthentication(App);
