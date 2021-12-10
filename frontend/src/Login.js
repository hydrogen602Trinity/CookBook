import { useEffect, useState, createRef, forwardRef } from 'react';
import Grow from '@material-ui/core/Grow';
import { useFetchAPI } from './util/fetchAPI';
import Button from '@mui/material/Button';
import useLogin from './util/login';
import * as React from 'react';
import "./Theme.scss"

import useBetterState from './util/classLikeState';
import TextField from '@mui/material/TextField';
import {
    useNavigate
  } from "react-router-dom";
import "./Login.scss";

export default function Login(props) {
    //const [,  ] = useState([]);
    const login = useLogin();
    const nav = useNavigate();
    useEffect(() => {
        login.checkLogin(user => {
            if (user) {
                nav('/home');
            }
        });
    }, [login, nav]);

    const init_state = {
        'password': '',
        'email': ''
    };
    const handleChange = (field) => (ev) => { setState({[field]: ev.target.value});}
    const [state, setState] = useBetterState(init_state);
    //const [showPass, setShowPass] = useState(false);
    
    return (
        <div className="frame page-main login-page">
        <div className="header">
            <h1>
                Recipe Book Login
            </h1>
        </div>
        <div className="main" id="content">
        <img src="./loginImage.jpg" alt="Cookbook Image" ></img>
        
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
                <Button variant="outlined" onClick ={() => login.doLogin(state).then(_ => nav('/home'))}> Login</Button>    
            </div>

        </div>
        </div>
        
    </div>
        
    )
}