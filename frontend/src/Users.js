import { fetchControlAPI, makeAuthErrorHandler, useFetchAPI } from './util/fetchAPI';
import { useEffect, useState } from 'react';
import { styled } from '@mui/material/styles';
import createTrigger from "react-use-trigger";
import useTrigger from "react-use-trigger/useTrigger";
import CircularProgress from '@material-ui/core/CircularProgress';
import { DataGrid } from '@mui/x-data-grid';

import SearchIcon from '@mui/icons-material/Search';
import InputBase from '@mui/material/InputBase';
import { IconButton } from "@material-ui/core";
import DeleteIcon from '@material-ui/icons/Delete';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';

import './Theme.scss';
import './Users.scss';
import { isInteger } from './util/util';
import { NewUser } from './components/Form';
import { useNavigate } from 'react-router';
import { useSnackbar } from './components/Snackbar';
// import { useSnackbar } from './components/Snackbar';


const updateUsersTrigger = createTrigger();

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


function Users() {
    const dispatchMsg = useSnackbar();
    const nav = useNavigate();
    const sendToLogin = () => {
        dispatchMsg({type: 'error', text: 'Authentication Required'});
        nav('/');
    };


    const modifyUser = makeAuthErrorHandler(async (data) => {
        let result = await fetchControlAPI('user', 'PUT', data);
        if (!isInteger(result)) {
            throw new Error('Expected PUT to return int, but got ' + result);
        }
        updateUsersTrigger();
        return result;
    }, sendToLogin);

    const createUser = makeAuthErrorHandler(async data => {
        let result = await fetchControlAPI('user', 'POST', data);
        updateUsersTrigger();
        return result;
    }, sendToLogin);

    const deleteUserByID = makeAuthErrorHandler(async id => {
        let result = null;
        if (isInteger(id)) {
            result = await fetchControlAPI('user/' + id, 'DELETE', null, false);
            updateUsersTrigger();
        }
        return result;
    }, sendToLogin);

    const updateUsersTriggerValue = useTrigger(updateUsersTrigger);
    const [ isLoading, userData, error ] = useFetchAPI('user', [updateUsersTriggerValue]);

    // useEffect(() => {
    //     if (error) {
    //         dispatchMsg({type: 'error', text: 'Failed to load users'});
    //     }
    //     // eslint-disable-next-line
    // }, [error]);

    const [users, setUsers] = useState([]);

    const [selectedRows, setSelectedRows] = useState([]);
    const [showForm, setShowForm] = useState(false);

    useEffect(() => {
        if (userData) {
            console.log('loading users: ',userData);
            setUsers(userData);
        }
    }, [userData]);

    const [search, setSearch] = useState('');

    return (
    <div className="users frame-footer">
        <div className="main" id="content">
        {isLoading ? 
            <div className="center"><CircularProgress className="circular-progress"/></div>
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
    </div>
    );
}

export default Users;