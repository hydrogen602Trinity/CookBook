import React from 'react';
import ReactDOM from 'react-dom';
import {
  BrowserRouter,
  Routes,
  Route,
  Link,
  useLocation,
  useNavigate
} from "react-router-dom";
import LocalizationProvider from '@mui/lab/LocalizationProvider';
import AdapterDateFns from '@mui/lab/AdapterDayjs';

// import './index.css';
// import App from './App';
//import Note from './Note';
import Recipes from './Recipes';
import Users from './Users';
import ErrorBounds from './components/ErrorBounds';
import { SnackbarComponent } from './components/Snackbar';
import useLogin from './util/login';
import Meals from './Meals';
// import { cleanQuotes } from './util/util';

import "./index.scss";
import { Button } from '@material-ui/core';

function Index() {
  const login = useLogin();

  return (      
  <div>
    <nav>
      <ul>
        <li>
          <Link to="/recipes">Recipes</Link>
        </li>
        <li>
          <Link to="/users">Users</Link>
        </li>
      </ul>
      </nav>
      <button onClick={() => login.doLogin({email: 'jrotter@trinity.edu', password: 'postgres'})}>Login Admin</button>
      <button onClick={() => login.doLogin({email: 'max.mustermann@t-online.de', password: 'postgres'})}>Login Default</button>
      <button onClick={login.doLogout}>Logout</button>
  </div>);
}

function NoMatch() {
  let location = useLocation();

  return (
    <div style={{padding: '1em'}}>
      <h1>404</h1>
      <h3>
        No match for <code>{location.pathname}</code>
      </h3>
    </div>
  );
}

function NavMenu() {
  const nav = useNavigate();

  return (
    <div className="route-menu">
      <Button variant="text" onClick={() => nav('/')}>Home</Button>
      <Button variant="text" onClick={() => nav('/recipes')}>Recipes</Button>
      <Button variant="text" onClick={() => nav('/meals')}>Meal Plan</Button>
    </div>
  );
}

ReactDOM.render(
  <React.StrictMode>
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <BrowserRouter>
        <ErrorBounds>
          <SnackbarComponent>
            <div className="routing">
              <div>
                <Routes>
                  <Route path="/" element={<Index/>}/>
                  <Route path="/recipes" element={<Recipes/>}/>
                  <Route path="/users" element={<Users/>}/>
                  <Route path="/meals" element={<Meals/>}/>
                  <Route path="*" element={<NoMatch />}/>
                </Routes>
              </div>
              <NavMenu />
            </div>
          </SnackbarComponent>

          
        </ErrorBounds>
      </BrowserRouter>
    </LocalizationProvider>
  </React.StrictMode>,
  document.getElementById('root')
);
