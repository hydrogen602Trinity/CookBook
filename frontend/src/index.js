import React, { useEffect } from 'react';
import ReactDOM from 'react-dom';
import {
  BrowserRouter,
  Routes,
  Route,
  Link,
  useSearchParams
} from "react-router-dom";
import { useState, forwardRef } from "react";
import Snackbar from '@material-ui/core/Snackbar';
import MuiAlert from '@material-ui/lab/Alert';
import Grow from '@material-ui/core/Grow';

// import './index.css';
// import App from './App';
//import Note from './Note';
import Recipes from './Recipes';
import Users from './Users';
import test from './test';
import ErrorBounds from './components/ErrorBounds';

const Alert = forwardRef((props, ref) => {
  return <MuiAlert ref={ref} elevation={6} variant="filled" {...props} />;
});

const GrowTransition = forwardRef((props, ref) => {
  return <Grow ref={ref} {...props} />;
});

function Index() {
  let [searchParams, setSearchParams] = useSearchParams();
  const authError = Boolean(searchParams.getAll('autherror').length);
  console.log();

  const [errMsg, setErrMsg] = useState('');
  const handleClose = () => setErrMsg('');

  useEffect(() => { if (errMsg) { setSearchParams({}); }}, [errMsg]);

  if (errMsg === '' && authError) {
    setErrMsg("Authentication Required");
  }

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
      <button onClick={test}>Login</button>
      <Snackbar 
        open={Boolean(errMsg)} 
        autoHideDuration={12000} 
        TransitionComponent={GrowTransition}
        onClose={handleClose}>
        <Alert onClose={handleClose} severity="error">
        {errMsg}
        </Alert>
      </Snackbar>
  </div>);
}

ReactDOM.render(
  <React.StrictMode>
    <BrowserRouter>
      <ErrorBounds>
        <Routes>
          <Route path="/" element={<Index/>}/>
          <Route path="/recipes" element={<Recipes/>}/>
          <Route path="/users" element={<Users/>}/>
        </Routes>
      </ErrorBounds>
    </BrowserRouter>
    
  </React.StrictMode>,
  document.getElementById('root')
);
