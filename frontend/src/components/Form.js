import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import OutlinedInput from '@mui/material/OutlinedInput';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import InputAdornment from '@mui/material/InputAdornment';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import IconButton from '@mui/material/IconButton';
import InputLabel from '@mui/material/InputLabel';
import FormControl from '@mui/material/FormControl';
import DatePicker from '@mui/lab/DatePicker';


import "./Form.scss";
import { useState, useEffect } from 'react';
import useBetterState from '../util/classLikeState';
import dayjs from 'dayjs';

// props need to have
// show => bool
// handleClose => fn that hides
// callback => fn that receives state

export function Select2Dates(props) {
    const handleClose = props.handleClose;
    const handleCreate = () => {
        props.callback([state1, state2]);
        handleClose();
        setState1(dayjs());
        setState2(dayjs());
    };

    const [state1, setState1] = useState(dayjs());
    const [state2, setState2] = useState(dayjs());

    const handleChange1 = value => { 
        setState1(value); 
    }

    const handleChange2 = value => { 
        setState2(value); 
    }

    useEffect(() => {
        if (props.show) {
            setState1(dayjs());
            setState2(dayjs());
        }
    }, [props.show]);

    return (
        <Dialog open={props.show} onClose={handleClose} maxWidth="sm" fullWidth className="date-popup">
            <DialogTitle>Select Start and End Day</DialogTitle>
            <DialogContent>
                <DatePicker
                    label="Start Day"
                    value={state1}
                    onChange={handleChange1}
                    renderInput={(params) => <TextField {...params} />}
                />
                <DatePicker
                    label="End Day"
                    value={state2}
                    onChange={handleChange2}
                    renderInput={(params) => <TextField {...params} />}
                />
            </DialogContent>
            <DialogActions>
              <Button onClick={handleClose}>Cancel</Button>
              <Button onClick={handleCreate}>Submit</Button>
            </DialogActions>
        </Dialog>
        );
}

export function MealNewDayPopup(props) {
    const init_state = '';
    const handleClose = props.handleClose;
    const handleCreate = () => {
        props.callback(state);
        handleClose();
        setState(init_state);
    };

    const [state, setState] = useState(dayjs());

    const handleChange = value => { 
        setState(value); 
    }

    useEffect(() => {
        if (props.show) {
            setState(dayjs());
        }
    }, [props.show]);

    return (
        <Dialog open={props.show} onClose={handleClose} maxWidth="sm" fullWidth className="meal-new-day-popup">
            <DialogTitle>New Day Meal Plan</DialogTitle>
            <DialogContent>
                {/* <TextField
                    autoFocus
                    margin="dense"
                    id="search-term"
                    label="Search Term"
                    fullWidth
                    variant="outlined"
                    value={state}
                    onChange={handleChange}
                /> */}
                <DatePicker
                    label="New Day"
                    value={state}
                    onChange={handleChange}
                    renderInput={(params) => <TextField {...params} />}
                />
            </DialogContent>
            <DialogActions>
              <Button onClick={handleClose}>Cancel</Button>
              <Button onClick={handleCreate}>Create</Button>
            </DialogActions>
        </Dialog>
        );
}

export function SearchPopup(props) {
    const init_state = '';

    const handleClose = props.handleClose;
    const handleCreate = () => {
        props.callback([state,ingredient]);
        handleClose();
        setState(init_state);
    };

    const [state, setState] = useState('');
    const [ingredient, setIngredient] = useState('');

    const handleChange = ev => { setState(ev.target.value); }

    return (
    <Dialog open={props.show} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>Search</DialogTitle>
        <DialogContent>   
            <TextField
                autoFocus
                margin="dense"
                id="search-term"
                label="Recipe"
                fullWidth
                variant="outlined"
                value={state}
                onChange={handleChange}
            />
            <TextField
                margin="dense"
                id="search-term2"
                label="Or Search by Ingredient"
                fullWidth
                variant="outlined"
                value={ingredient}
                onChange={ev => setIngredient(ev.target.value)}
            />
            {/* <Box sx={{ display: 'flex', alignItems: 'flex-end' }}>
                <SearchIcon sx={{ color: 'action.active', mr: 1, my: 0.5 }} />
                
            </Box> */}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleCreate}>Search</Button>
        </DialogActions>
    </Dialog>
    );
}

export function NewUser(props) {
    const handleClose = props.handleClose;
    const handleCreate = () => {
        props.callback(state);
        handleClose();
        setState(init_state);
    };

    const [showPass, setShowPass] = useState(false);

    const init_state = {
        'name': '',
        'password': '',
        'email': ''
    };
    const [state, setState] = useBetterState(init_state);

    const handleClickShowPassword = () => {
        setShowPass(!showPass);
    };
    
    const handleMouseDownPassword = (event) => {
        event.preventDefault();
    };

    const handleChange = (field) => (ev) => { setState({[field]: ev.target.value}); }

    return (
        // <div className="center form-component">
    <Dialog open={props.show} onClose={handleClose}>
        <DialogTitle>New User</DialogTitle>
        <DialogContent>
            <DialogContentText>
                Please enter the following information to create a new user
            </DialogContentText>
            <TextField
                autoFocus
                margin="dense"
                id="new-user-name"
                label="Name"
                fullWidth
                variant="outlined"
                value={state.name}
                onChange={handleChange('name')}
            />
            <TextField
                margin="dense"
                id="new-user-email"
                label="Email Address"
                type="email"
                fullWidth
                variant="outlined"
                value={state.email}
                onChange={handleChange('email')}
            />
            <FormControl fullWidth sx={{ 
                    m: 1, 
                    marginLeft: 0,
                    marginRight: 0,
                    marginTop: '8px',
                    marginBottom: '4px'
                }} variant="outlined">
                <InputLabel htmlFor="new-user-password">Password</InputLabel>
                <OutlinedInput
                    margin="dense"
                    id="new-user-password"
                    label="Password"
                    type={showPass ? 'text' : 'password'}
                    variant="outlined"
                    value={state.password}
                    onChange={handleChange('password')}
                
                endAdornment={
                <InputAdornment position="end">
                    <IconButton
                    aria-label="toggle password visibility"
                    onClick={handleClickShowPassword}
                    onMouseDown={handleMouseDownPassword}
                    edge="end"
                    >
                    {showPass ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                </InputAdornment>
                }/>
            </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleCreate}>Create</Button>
        </DialogActions>
    </Dialog>
        // </div>
    );
}