import React from 'react';
import ReactDOM from 'react-dom';
import {
  BrowserRouter,
  Routes,
  Route,
  Link
} from "react-router-dom";

// import './index.css';
// import App from './App';
//import Note from './Note';
import Recipes from './Recipes';
import Users from './Users';
import ErrorBounds from './components/ErrorBounds';
import { SnackbarComponent } from './components/Snackbar';
import useLogin from './util/login';
// import { cleanQuotes } from './util/util';

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

ReactDOM.render(
  <React.StrictMode>
    <BrowserRouter>
      <ErrorBounds>
        <SnackbarComponent>
          <Routes>
            <Route path="/" element={<Index/>}/>
            <Route path="/recipes" element={<Recipes/>}/>
            <Route path="/users" element={<Users/>}/>
          </Routes>
        </SnackbarComponent>
      </ErrorBounds>
    </BrowserRouter>
    
  </React.StrictMode>,
  document.getElementById('root')
);
