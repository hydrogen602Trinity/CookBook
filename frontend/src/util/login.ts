import { useCallback } from "react";
import { useSnackbar } from "../components/Snackbar";
import { fetchControlAPI2 } from './fetchAPI';
import { cleanQuotes } from './util';


export interface ILoginData {
    email: string,
    password: string
}


export default function useLogin() {
    const dispatchMsg = useSnackbar();

    const checkLogin = useCallback(() => 
        fetchControlAPI2('login', 'GET')
            .then(response => response.json()).then(user => user as (string | null)).catch(err => {
                dispatchMsg({type: 'error', text: `Login Status Check Failed: ${err.message}`});
                return null;
            }
        ), [dispatchMsg]);

    const doLogin = useCallback((data: ILoginData) =>
        fetchControlAPI2('login', 'POST', data)
            .then(response =>
                response.text().then(preText => {
                    let text = cleanQuotes(preText);
                    if (response.ok) {
                        dispatchMsg({type: 'success', text: `Welcome ${text}`});
                    }
                    else {
                        dispatchMsg({type: 'error', text: `Login Failed: ${text}`});
                    }
                    return text;
                })
            ).catch(err => {
                dispatchMsg({type: 'error', text: `Login Failed: ${err.message}`});
                return null;
            }
        // eslint-disable-next-line
        ), []);

    const doLogout = useCallback(() =>
        fetchControlAPI2('login', 'DELETE')
            .then(response =>
                response.text().then(preText => {
                    let text = cleanQuotes(preText);
                    if (response.ok) {
                        dispatchMsg({type: 'success', text: 'Successfully logged out'});
                    }
                    else {
                        dispatchMsg({type: 'error', text: `Logout Failed: ${text}`});
                    }
                    return text;
                })
            ).catch(err => {
                dispatchMsg({type: 'error', text: `Logout Failed: ${err.message}`});
                return null;
            }
        // eslint-disable-next-line
        ), []);;
    

    return {doLogin: doLogin, doLogout: doLogout, checkLogin: checkLogin};
}