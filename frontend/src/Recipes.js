import RecipeEntry from './components/RecipeEntry';
import './Recipes.css'
import './root.css'
import { useFetchAPI } from './util/fetchAPI';
import Snackbar from '@material-ui/core/Snackbar';
import MuiAlert from '@material-ui/lab/Alert';
import Grow from '@material-ui/core/Grow';
import CircularProgress from '@material-ui/core/CircularProgress';
import { useEffect, useState, createRef, forwardRef } from 'react';
import createTrigger from "react-use-trigger";
import useTrigger from "react-use-trigger/useTrigger";


const updateRecipesTrigger = createTrigger();

const Alert = forwardRef((props, ref) => {
    return <MuiAlert ref={ref} elevation={6} variant="filled" {...props} />;
});

const GrowTransition = forwardRef((props, ref) => {
    return <Grow ref={ref} {...props} />;
});


export default function Recipes() {
    const [state, setState] = useState({snackbar: null});
    const snackbarRef = createRef(null);

    const updateRecipesTriggerValue = useTrigger(updateRecipesTrigger);
    
    const [ isLoading, recipes, error ] = useFetchAPI('recipe', [updateRecipesTriggerValue]);

    useEffect(() => setState({snackbar: (error ? 'Failed to load recipes' : null)}), [error]);

    const handleClose = (event, reason) => {
        if (reason === 'clickaway') {
            return;
        }
        setState({snackbar: null});
    };

    // const setSnackbar = (msg) => {
    //     setState({snackbar: null});
    // };

    console.log(recipes, isLoading);

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
                {isLoading ? 
                    <CircularProgress className="recipe-circular-progress"/> : 
                    recipes.map(recipe => <RecipeEntry key={recipe.id} recipe={recipe}/>)}
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