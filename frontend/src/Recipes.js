import RecipeEntry from './components/RecipeEntry';
import './Recipes.scss';
import './Theme.scss';
import './root.css';
import { useFetchAPI } from './util/fetchAPI';
import CircularProgress from '@material-ui/core/CircularProgress';
import { useEffect, useState } from 'react';
import createTrigger from "react-use-trigger";
import useTrigger from "react-use-trigger/useTrigger";
// import RecipeEditor from './components/RecipeEditor';


const updateRecipesTrigger = createTrigger();


export default function Recipes() {
    const updateRecipesTriggerValue = useTrigger(updateRecipesTrigger);
    const [ isLoading, recipesData, error ] = useFetchAPI('recipe', [updateRecipesTriggerValue]);

    const [recipes, setRecipes] = useState([]);

    useEffect(() => {
        if (recipesData) {
            console.log('loading recipes: ',recipesData);
            setRecipes(recipesData);
        }
    }, [recipesData]);

    function addRecipe() {
        const newRecipe = {
            name: '',
            notes: '',
            ingredients: [],
        };
        setRecipes((prevRecipes) => [...prevRecipes, newRecipe])
    }

    console.log(recipes, isLoading);

    return (
        <div className="frame recipes-main">
            <div className="header">
                <h1>
                    Recipe Book
                </h1>
                <button onClick={addRecipe}>
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
                    <CircularProgress className="circular-progress"/>
                : 
                    recipes.map((recipe, i) => 
                        <RecipeEntry 
                            key={(recipe.id) ? `id=${recipe.id}` : `idx=${i}`} 
                            recipe={recipe} 
                            updateRecipesTrigger={updateRecipesTrigger}
                            />)
                }
            </div>
        </div>
    );
}