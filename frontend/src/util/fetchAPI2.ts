import { useCallback } from "react";
import { useNavigate } from "react-router";
import { useSnackbar } from "../components/Snackbar";
import { fetchControlAPI, AuthError, APIError } from './fetchAPI';

// callback is given data
export function useFetchControlAPI(path: string, method: 'GET' | 'PUT' | 'POST' | 'DELETE', callback: (data: any) => void, json: boolean = true) {
    const dispatchMsg = useSnackbar();
    const nav = useNavigate();
    const sendToLogin = () => {
        dispatchMsg({type: 'error', text: 'Authentication Required'});
        nav('/');
    };

    
    
    return useCallback(async (data: any) => {
        let result = null;
        try {
            result = await fetchControlAPI(path, method, data, json);
        }
        catch (err) {
            if (err instanceof AuthError) {
                sendToLogin();
                return null;
            }
            else if (err instanceof APIError) {
                dispatchMsg({type: 'error', text: 'Something went wrong'});
                return null;
            }
            else {
                throw err;
            }
        }

        return callback(result);
    }, [path, method, json]);
}