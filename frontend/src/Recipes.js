import RecipeEntry from './components/RecipeEntry';
import './Recipes.scss';
import './Theme.scss';
import './root.css';
import { useFetchAPI } from './util/fetchAPI';
import CircularProgress from '@material-ui/core/CircularProgress';
import { useEffect, useRef, useState } from 'react';
import createTrigger from "react-use-trigger";
import useTrigger from "react-use-trigger/useTrigger";
import Button from '@mui/material/Button';

import { SearchPopup } from './components/Form';
import { Slide } from '@mui/material';
import { TransitionGroup } from 'react-transition-group';
import Collapse from '@mui/material/Collapse';

// import RecipeEditor from './components/RecipeEditor';


const updateRecipesTrigger = createTrigger();


export default function Recipes() {
    const [searchTerm, setSearchTerm] = useState(['', '']);
    const updateRecipesTriggerValue = useTrigger(updateRecipesTrigger);

    const [ isLoading, recipesData, error ] = useFetchAPI((() => {
        const [recipe, ingredient] = searchTerm;

        const r = recipe ? `search=${encodeURIComponent(recipe)}` : '';
        const i = ingredient ? `searchi=${encodeURIComponent(ingredient)}` : '';

        const prefix = 'recipe' + ((r || i) ? '?' : '');

        return prefix + r + ((r && i) ? '&' : '') + i;
    })(), [updateRecipesTriggerValue]);

    const [recipes, setRecipes] = useState([]);

    useEffect(() => {
        if (recipesData) {
            console.log('loading recipes: ',recipesData);
            setRecipes(recipesData);
        }
    }, [recipesData]);

    useEffect(() => {
        // somehow sticking this into useFetchAPI's dependencies doesn't work
        updateRecipesTrigger();
    }, [searchTerm])

    function addRecipe() {
        const newRecipe = {
            name: '',
            notes: '',
            ingredients: [],
        };
        setRecipes((prevRecipes) => [...prevRecipes, newRecipe])
    }

    const [showSearch, setShowSearch] = useState(false);

    const ref = useRef(null);

    return (
        <div className="frame recipes-main">
            <div className="header" ref={ref}>
                <h1>
                    Recipe Book
                </h1>
                <div className="actions">
                    <Button className="actions-buttons" onClick={() => setShowSearch(true)}>
                        <i className="fas fa-search" style={{color: 'black'}}></i>
                    </Button>
                    <Button className="actions-buttons" onClick={addRecipe}>
                        <i className="fas fa-plus" style={{color: 'black'}}></i>
                    </Button>
                </div>
            </div>
            {/* <div className="bar" hidden={true}>
                <button>New</button>
                <button>Edit</button>
                <button>Delete</button>
            </div> */}

            <div className="main" id="content">
                <TransitionGroup>
                    {(searchTerm[0] || searchTerm[1])  ? 
                    <Slide direction="down" container={ref.current}>
                        <div className="search-term">
                            <div>
                                <span>
                                    <Button className="actions-buttons" onClick={() => setShowSearch(true)}>
                                        <i className="fas fa-search" style={{color: 'black'}}></i>
                                    </Button>
                                    {searchTerm[0]}
                                </span>
                                <Button onClick={() => setSearchTerm(['', ''])}>
                                    <i className="fas fa-times"></i>
                                </Button>
                            </div>
                            {searchTerm[1] ? 
                            <div>
                                <span>Ingredient: {searchTerm[1]}</span>
                            </div>
                            : null}
                        </div>
                    </Slide>
                    : null }
                </TransitionGroup>
                {isLoading ? 
                    <CircularProgress className="circular-progress"/>
                : 
                <TransitionGroup>
                    {recipes.map((recipe, i) => 
                        <Collapse key={(recipe.id) ? `id=${recipe.id}` : `idx=${i}`} >
                            <RecipeEntry 
                                recipe={recipe} 
                                updateRecipesTrigger={updateRecipesTrigger}
                                />
                        </Collapse>)}
                </TransitionGroup>
                }
            </div>
            <SearchPopup 
                show={showSearch} 
                handleClose={() => setShowSearch(false)}
                callback={setSearchTerm}
            />
        </div>
    );
}