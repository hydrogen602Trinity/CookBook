import { useEffect, useState, createRef, forwardRef } from 'react';
import Grow from '@material-ui/core/Grow';
import { useFetchAPI } from './util/fetchAPI';
import Button from '@mui/material/Button';
import useLogin from './util/login';
import * as React from 'react';


import useBetterState from './util/classLikeState';
import TextField from '@mui/material/TextField';
import {
    BrowserRouter,
    Routes,
    Route,
    Link,
    useSearchParams
  } from "react-router-dom";
import "./Login.scss";

export default function Login(props) {
    //const [,  ] = useState([]);
    
    const init_state = {
        'password': '',
        'email': ''
    };
    const handleChange = (field) => (ev) => { setState({[field]: ev.target.value});}
    const [state, setState] = useBetterState(init_state);
    const [showPass, setShowPass] = useState(false);
    
    return (
        <div className="loginNav frame-footer"> 
            
            <div className = "loginComponent">
                
                <TextField
                    margin="dense"
                    id="user-email"
                    label="Email Address"
                    type="email"
                    fullWidth
                    variant="outlined"
                    value={state.email}
                    onChange={handleChange('email')}
                />
                <TextField
                    autoFocus
                    margin="dense"
                    id="user-password"
                    label="Password"
                    type="password"
                    fullWidth
                    variant="outlined"
                    value={state.name}
                    onChange={handleChange('password')}

                />
                <Button variant="outlined" onClick ={() => login.doLogin(state)}> Login</Button>    
            </div>

        </div>
    )
}