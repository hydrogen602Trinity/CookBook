import { createContext, forwardRef, useContext, useReducer } from 'react';
import { Snackbar } from '@mui/material';
import MuiAlert from '@mui/material/Alert';


const Alert = forwardRef((props, ref) => 
    <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />
  );

const SnackbarContext = createContext();
// this will return dispatchMsg with arguments of state
export const useSnackbar = () => useContext(SnackbarContext);


const initialState = {type: null, text: ''};

function reducer(state, action) {
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

function getAutoHideDuration(state) {
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


export function SnackbarComponent(props) {
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
            <Alert onClose={handleClose} severity={state.type} sx={{ width: '100%' }}>
                {state.text}
            </Alert>
        </Snackbar>
    </SnackbarContext.Provider>
    );
}