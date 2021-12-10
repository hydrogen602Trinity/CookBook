import { useEffect, useState, createRef, forwardRef } from 'react';
import { fetchControlAPI, makeAuthErrorHandler, useFetchAPI } from './util/fetchAPI';
import Grow from '@material-ui/core/Grow';
import createTrigger from "react-use-trigger";
import useTrigger from "react-use-trigger/useTrigger";
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
//import "./Users"
import { NewUser } from './components/Form';
import { useSnackbar } from './components/Snackbar';


export default function Login(props) {
    //const [,  ] = useState([]);
    const login = useLogin();
    const updateUsersTrigger = createTrigger();
    const dispatchMsg = useSnackbar();
    const sendToLogin = () => {
        dispatchMsg({type: 'error', text: 'Authentication Required'});
        nav('/');
    };
    const nav = useNavigate();
    useEffect(() => {
        login.checkLogin(user => {
            if (user) {
                nav('/home');
            }
        });
    }, [login, nav]);

    const createUser = makeAuthErrorHandler(async data => {
        let result = await fetchControlAPI('account', 'POST', data);
        updateUsersTrigger();
        return result;
    }, sendToLogin);

    const init_state = {
        'password': '',
        'email': ''
    };
    const handleChange = (field) => (ev) => { setState({[field]: ev.target.value});}
    const [state, setState] = useBetterState(init_state);
    const [showForm, setShowForm] = useState(false);
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
                <NewUser 
                    show={showForm} 
                    handleClose={() => setShowForm(false)} 
                    callback={createUser}
                    />
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
                <Button variant="text" onClick ={() => setShowForm(true)}> New User</Button>     
            </div>

        </div>
        </div>
        
    </div>
        
    )
}