import { createContext, forwardRef, useContext, useReducer, ReactNode } from 'react';
import { Snackbar } from '@mui/material';
import MuiAlert from '@mui/material/Alert';


export interface ISnackbarMsg {
    type: 'error' | 'warning' | 'info' | 'success' | null,
    text: string
}


const SnackbarContext = createContext((msg: ISnackbarMsg) => {});
// this will return dispatchMsg with arguments of state
export const useSnackbar = () => useContext(SnackbarContext);


const initialState: ISnackbarMsg = {type: null, text: ''};

function reducer(_: ISnackbarMsg, action: ISnackbarMsg) {
    if (typeof action.text !== 'string') {
        throw new TypeError(`SnackBar: Expected string for text, but got ${action.text}`)
    }
    const clean = {type: action.type, text: action.text};

    switch (clean.type) {
        case 'error':
            return clean;
        case 'warning':
            return clean;
        case 'info':
            return clean;
        case 'success':
            return clean;
        case null:
            return {type: null, text: ''};
        default:
            throw new TypeError(`SnackBar: Unexpected value for type, got ${clean.type}`);
    }
}

function getAutoHideDuration(state: ISnackbarMsg): number | null {
    switch (state.type) {
        case 'error':
            return null; // never auto hide    
        case 'warning':
            return null; // never auto hide  
        case 'info':
            return 12000; // 12 sec
        case 'success':
            return 6000; // 6 sec
        case null:
            return null;
        default:
            throw new TypeError(`SnackBar: Unexpected value for type, got ${state.type}`);
    }
}


export interface IProps {
    children: ReactNode
}

export function SnackbarComponent(props: IProps) {
    const [state, dispatchMsg] = useReducer(reducer, initialState);

    const handleClose = () => {
        dispatchMsg(initialState);
    }

    return (
    <SnackbarContext.Provider value={dispatchMsg}>
        {props.children}
        <Snackbar 
            open={Boolean(state.type)} 
            autoHideDuration={getAutoHideDuration(state)} 
            onClose={handleClose}
            key={state.text} // correct?
            anchorOrigin={{vertical: 'bottom', horizontal: 'center'}}>
            <MuiAlert elevation={6} variant="filled" onClose={handleClose} severity={state.type === null ? undefined : state.type} sx={{ width: '100%' }}>
                {state.text}
            </MuiAlert>
        </Snackbar>
    </SnackbarContext.Provider>
    );
}