import { useFetchAPI } from './util/fetchAPI';
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

const SearchIconWrapper = styled('div')(({ theme }) => ({
    padding: theme.spacing(0, 2),
    height: '100%',
    position: 'absolute',
    pointerEvents: 'none',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  }));

const Search = styled('div')(({ theme }) => ({
    position: 'relative',
    borderRadius: theme.shape.borderRadius,
    backgroundColor: alpha(theme.palette.common.white, 0.15),
    '&:hover': {
      backgroundColor: alpha(theme.palette.common.white, 0.25),
    },
    marginRight: theme.spacing(2),
    marginLeft: 0,
    width: '100%',
    [theme.breakpoints.up('sm')]: {
      marginLeft: theme.spacing(3),
      width: 'auto',
    },
  }));

const StyledInputBase = styled(InputBase)(({ theme }) => ({
    color: 'inherit',
    '& .MuiInputBase-input': {
      padding: theme.spacing(1, 1, 1, 0),
      // vertical padding + font size from searchIcon
      paddingLeft: `calc(1em + ${theme.spacing(4)})`,
      transition: theme.transitions.create('width'),
      width: '100%',
      [theme.breakpoints.up('md')]: {
        width: '20ch',
      },
    },
  }));

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

    const [search, setSearch] = useState('');

    return (
    <div>
        <div className="main" id="content">
        {isLoading ? 
            <CircularProgress className="recipe-circular-progress"/>
        : 
            <div>
                <Search>
                    <SearchIconWrapper>
                        <SearchIcon />
                    </SearchIconWrapper>
                    <StyledInputBase
                        placeholder="Search…"
                        inputProps={{ 'aria-label': 'search' }}
                        onChange={(ev) => setSearch(ev.target.value.toLowerCase())}
                        value={search}
                    />
                </Search>
                <div style={{ height: 400, width: '100%' }}>
                    <DataGrid
                        rows={users.filter(obj => obj.name.toLowerCase().includes(search))}
                        columns={columns}
                        pageSize={25}
                        rowsPerPageOptions={[25]}
                        checkboxSelection
                    />
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