import RecipeEntry from './parts/RecipeEntry';
import './Recipes.css'
import { useAPIState } from './util/fetchAPI';
import Snackbar from '@material-ui/core/Snackbar';
import MuiAlert from '@material-ui/lab/Alert';
import Grow from '@material-ui/core/Grow';
import { useEffect, useState, createRef, forwardRef } from 'react';

const Alert = forwardRef((props, ref) => {
    return <MuiAlert ref={ref} elevation={6} variant="filled" {...props} />;
});

const GrowTransition = forwardRef((props, ref) => {
    return <Grow ref={ref} {...props} />;
});


export default function Recipes() {
    const [state, setState] = useState({snackbar: null});
    const [recipes, updateRecipes] = useAPIState('recipe', 
        e => setState({snackbar: 'Failed to load recipes'}));
    const snackbarRef = createRef(null);

    const handleClose = (event, reason) => {
        if (reason === 'clickaway') {
            return;
        }
        setState({snackbar: null});
    };

    const setSnackbar = (msg) => {
        setState({snackbar: null});
    };

    console.log(recipes);

    return (
        <div className="frame">
            <div className="header">
                <h1>
                    Recipe Book
                </h1>
                <button onClick={() => console.log('yeet')}>
                    <i className="fas fa-plus"></i>
                </button>
            </div>
            {/* <div className="bar" hidden={true}>
                <button>New</button>
                <button>Edit</button>
                <button>Delete</button>
            </div> */}
            <div className="main" id="content">
                {recipes.map(recipe => <RecipeEntry key={recipe.id} recipe={recipe}/>)}
            </div>
            {/* <div className="sidebar" hidden={true}>
                <button onClick={() => console.log('getAllRecipes')}>
                    Recipes
                </button>
            </div> */}
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