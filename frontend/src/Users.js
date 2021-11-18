import { fetchControlAPI, useFetchAPI } from './util/fetchAPI';
import { useEffect, useState, createRef, forwardRef } from 'react';
import { styled, alpha } from '@mui/material/styles';
import Snackbar from '@material-ui/core/Snackbar';
import createTrigger from "react-use-trigger";
import useTrigger from "react-use-trigger/useTrigger";
import CircularProgress from '@material-ui/core/CircularProgress';
import MuiAlert from '@material-ui/lab/Alert';
import Grow from '@material-ui/core/Grow';
import { DataGrid } from '@mui/x-data-grid';

import SearchIcon from '@mui/icons-material/Search';
import InputBase from '@mui/material/InputBase';
import { IconButton } from "@material-ui/core";
import DeleteIcon from '@material-ui/icons/Delete';
import EditIcon from '@material-ui/icons/Edit';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';

import './Theme.scss';
import './Users.scss';
import { isInteger } from './util/util';
import { NewUser } from './components/Form';


const updateUsersTrigger = createTrigger();

const Alert = forwardRef((props, ref) => {
    return <MuiAlert ref={ref} elevation={6} variant="filled" {...props} />;
});

const GrowTransition = forwardRef((props, ref) => {
    return <Grow ref={ref} {...props} />;
});

const columns = [
    { field: 'id', headerName: 'ID', flex: 90 },
    { field: 'name', headerName: 'Name', flex: 250, editable: true },
    { field: 'email', headerName: 'Email', flex: 250, editable: true },
];

const StyledInputBase = styled(InputBase)(({ theme }) => ({
    color: 'inherit',
    '& .MuiInputBase-input': {
      padding: theme.spacing(1, 1, 1, 0),
      // vertical padding + font size from searchIcon
    //   paddingLeft: `calc(1em + ${theme.spacing(4)})`,
      transition: theme.transitions.create('width'),
      width: '100%',
      [theme.breakpoints.up('md')]: {
        width: '20ch',
      },
    },
  }));


async function deleteUserByID(id) {
    let result = null;
    if (isInteger(id)) {
        console.log('deleting...');
        try {
            result = await fetchControlAPI('user/' + id, 'DELETE', null, false);
            console.log('deleted');
            // setState({
            //     name: '',
            //     notes: '',
            //     ingredients: [],
            // });
            //if (!no_update) {
            updateUsersTrigger();
            //}
        }
        catch (err) {
            console.error('deleteThis', err);
            // setError(err + '');
            throw err;
        }
    }
    return result;
}


async function modifyUser(data) {
    let result = null;
    try {
        result = await fetchControlAPI('user', 'PUT', data);
        if (!isInteger(result)) {
            throw new Error('Expected PUT to return int, but got ' + result);
        }
        updateUsersTrigger();
    }
    catch (err) {
        console.error('modifyUser', err);
        // setError(err + '');
        throw err;
    }
    
    console.log('response', result);
    return result;
}


async function createUser(data) {
    let result = null;
    try {
        result = await fetchControlAPI('user', 'POST', data);
        updateUsersTrigger();
    }
    catch (err) {
        console.error('createUser', err);
        // setError(err + '');
        throw err;
    }
    
    console.log('response', result);
    return result;
}


function Users() {
    const snackbarRef = createRef(null);

    const [state, setState] = useState({
        snackbar: null
    });

    const updateUsersTriggerValue = useTrigger(updateUsersTrigger);
    const [ isLoading, userData, error ] = useFetchAPI('user', [updateUsersTriggerValue]);

    useEffect(() => setState({snackbar: (error ? 'Failed to load recipes' : null)}), [error]);

    const [users, setUsers] = useState([]);

    const [selectedRows, setSelectedRows] = useState([]);
    const [showForm, setShowForm] = useState(false);

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

    const [search, setSearch] = useState('');

    return (
    <div className="users frame-footer">
        <div className="main" id="content">
        {isLoading ? 
            <CircularProgress className="recipe-circular-progress center"/>
        : 
            <div>
                <NewUser 
                    show={showForm} 
                    handleClose={() => setShowForm(false)} 
                    callback={createUser}
                    />
                <div className="menu">
                    {/* <div style={{width: '1rem'}}></div> */}
                    <div className="search">
                        <div className="searchIcon">
                            <SearchIcon />
                        </div>
                        <StyledInputBase
                            placeholder="Search…"
                            inputProps={{ 'aria-label': 'search' }}
                            onChange={(ev) => setSearch(ev.target.value.toLowerCase())}
                            value={search}
                        />
                    </div>
                    <div style={{width: '50%'}}></div>
                    <IconButton onClick={() => setShowForm(true)}>
                        <AddCircleOutlineIcon className="icon" />
                    </IconButton>
                    {/* <IconButton onClick={() => console.log('edit!')}>
                        <EditIcon className="icon" />
                    </IconButton> */}
                    <IconButton onClick={() => {
                            const user_ids = selectedRows //.map(i => users[i-1].id);
                            user_ids.forEach(deleteUserByID)
                        }}>
                        <DeleteIcon className="icon" />
                    </IconButton>
                </div>
                <div className="table">
                    <DataGrid
                        rows={users.filter(obj => obj.name.toLowerCase().includes(search))}
                        columns={columns}
                        pageSize={25}
                        rowsPerPageOptions={[25]}
                        checkboxSelection
                        onSelectionModelChange={setSelectedRows}
                        onCellEditCommit={ev => {
                            let data = {id: ev.id};
                            data[ev.field] = ev.value;
                            modifyUser(data);
                        }}
                    /> {/* onCellValueChange */}
                </div>
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