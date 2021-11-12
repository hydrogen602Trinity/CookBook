import { useFetchAPI } from './util/fetchAPI';
import { useEffect, useState, createRef, forwardRef } from 'react';
import Snackbar from '@material-ui/core/Snackbar';
import createTrigger from "react-use-trigger";
import useTrigger from "react-use-trigger/useTrigger";
import CircularProgress from '@material-ui/core/CircularProgress';
import MuiAlert from '@material-ui/lab/Alert';
import Grow from '@material-ui/core/Grow';
import { DataGrid } from '@mui/x-data-grid';


const updateUsersTrigger = createTrigger();

const Alert = forwardRef((props, ref) => {
    return <MuiAlert ref={ref} elevation={6} variant="filled" {...props} />;
});

const GrowTransition = forwardRef((props, ref) => {
    return <Grow ref={ref} {...props} />;
});

const columns = [
    { field: 'id', headerName: 'ID', flex: 90 },
    { field: 'name', headerName: 'Name', flex: 250 },
    { field: 'email', headerName: 'Email', flex: 250 },
];

function Users() {
    const snackbarRef = createRef(null);

    const [state, setState] = useState({
        snackbar: null
    });

    const updateUsersTriggerValue = useTrigger(updateUsersTrigger);
    const [ isLoading, userData, error ] = useFetchAPI('user', [updateUsersTriggerValue]);

    useEffect(() => setState({snackbar: (error ? 'Failed to load recipes' : null)}), [error]);

    const [users, setUsers] = useState([]);

    useEffect(() => {
        if (userData) {
            console.log('loading users: ',userData);
            setUsers(userData);
        }
    }, [userData]);

    const handleClose = (event, reason) => {
        if (reason === 'clickaway') {
            return;
        }
        setState({snackbar: null});
    };

    return (
    <div>
        <div className="main" id="content">
        {isLoading ? 
            <CircularProgress className="recipe-circular-progress"/>
        : 
            <div style={{ height: 400, width: '100%' }}>
                <DataGrid
                    rows={users}
                    columns={columns}
                    pageSize={25}
                    rowsPerPageOptions={[25]}
                    checkboxSelection
                />
            </div>
        }
        </div>
        <Snackbar 
                ref={snackbarRef} 
                open={Boolean(state.snackbar)} 
                autoHideDuration={12000} 
                TransitionComponent={GrowTransition}
                onClose={handleClose}>
                <Alert onClose={handleClose} severity="error">
                {state.snackbar}
                </Alert>
            </Snackbar>
    </div>
    );
}

export default Users;