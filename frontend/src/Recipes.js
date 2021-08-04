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
// import RecipeEditor from './components/RecipeEditor';


const updateRecipesTrigger = createTrigger();

const Alert = forwardRef((props, ref) => {
    return <MuiAlert ref={ref} elevation={6} variant="filled" {...props} />;
});

const GrowTransition = forwardRef((props, ref) => {
    return <Grow ref={ref} {...props} />;
});


export default function Recipes() {
    const [state, setState] = useState({
        snackbar: null,
    });
    const snackbarRef = createRef(null);

    const updateRecipesTriggerValue = useTrigger(updateRecipesTrigger);
    const [ isLoading, recipesData, error ] = useFetchAPI('recipe', [updateRecipesTriggerValue]);

    useEffect(() => setState({snackbar: (error ? 'Failed to load recipes' : null)}), [error]);

    const handleClose = (event, reason) => {
        if (reason === 'clickaway') {
            return;
        }
        setState({snackbar: null});
    };

    const [recipes, setRecipes] = useState([]);

    useEffect(() => {
        if (recipesData) {
            console.log('loading recipes: ', recipesData);
            setRecipes(recipesData.map(e => { return {recipe: e, expanded: false} }));
        }
    }, [recipesData]);

    function addRecipe() {
        const newRecipe = {
            name: '',
            notes: '',
            ingredients: [],
        };
        setRecipes((prevRecipes) => [...prevRecipes, newRecipe]);
    }

    // console.log(recipes, isLoading);

    function setExpanded(idx, value) {
        console.log(idx, value);
        setRecipes(prevRecipes => {
            return prevRecipes.map(({recipe, expanded}, i) => {
                if (i == idx) {
                    return {recipe: recipe, expanded: value};
                }
                return {recipe: recipe, expanded: false};
            });
        })
    }

    return (
        <div className="frame">
            <div className="header">
                <h1>
                    Recipe Book
                </h1>
                <button onClick={addRecipe}>
                    <i className="fas fa-plus"></i>
                </button>
            </div>
            <div className="main" id="content">
                {isLoading ? 
                    <CircularProgress className="recipe-circular-progress"/>
                : 
                    recipes.map(({recipe, expanded}, i) => 
                        <RecipeEntry 
                            key={(recipe.id) ? `id=${recipe.id}` : `idx=${i}`} 
                            recipe={recipe} 
                            updateRecipesTrigger={updateRecipesTrigger}
                            isExpanded={expanded}
                            setExpanded={(value) => setExpanded(i, value)}
                            />)
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