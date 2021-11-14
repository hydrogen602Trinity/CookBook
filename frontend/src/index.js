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

ReactDOM.render(
  <React.StrictMode>
    <BrowserRouter>
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
      </div>
      <Routes>
        <Route path="/recipes" element={<Recipes/>}/>
        <Route path="/users" element={<Users/>}/>
      </Routes>
    </BrowserRouter>
    
  </React.StrictMode>,
  document.getElementById('root')
);
