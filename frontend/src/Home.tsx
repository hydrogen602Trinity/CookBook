import "./Home.scss"
import "./Theme.scss"
import Button from '@mui/material/Button';
import useLogin from "./util/login";
import { useSnackbar } from "./components/Snackbar";
import { useNavigate } from "react-router";
import { useEffect } from "react";
import createTrigger from "react-use-trigger";
import useTrigger from "react-use-trigger/useTrigger";

const checkLoginTrigger = createTrigger();

export default function Home() {
    const checkLoginTriggerValue = useTrigger(checkLoginTrigger);

    const login = useLogin();
    const dispatchMsg = useSnackbar();
    const nav = useNavigate();
    const sendToLogin = () => {
        dispatchMsg({type: 'error', text: 'Authentication Required'});
        nav('/');
    };

    useEffect(() => {
        login.checkLogin(user => {
            if (!user) {
                sendToLogin();
            }
        });
    }, [checkLoginTriggerValue, login]);

    return (
    <div className="frame page-main">
        <div className="header">
            <h1>
                Home
            </h1>
            <div className="actions">
                <Button className="actions-buttons" onClick={login.doLogout}>
                    <i className="fas fa-sign-out-alt" style={{color: 'black'}}></i>
                </Button>
            </div>
        </div>
        
        <div className="main" id="content">

        </div>
    </div>
    )
}