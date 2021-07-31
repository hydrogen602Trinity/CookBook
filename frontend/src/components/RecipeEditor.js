/*import { useState } from "react";
import './RecipeEditor.css'
import '../root.css'
import { colors } from '../root.js'
import TextField from '@material-ui/core/TextField';
import {
    withStyles,
  } from '@material-ui/core/styles';

const CssTextField = withStyles({
    root: {
      '& label.Mui-focused': {
        color: colors.darkGray,
      },
      '& .MuiOutlinedInput-root': {
        '&.Mui-focused fieldset': {
          borderColor: colors.darkGray,
        },
      },
    },
  })(TextField);


function RecipeEditor(props) {
    const [recipe, setRecipe] = useState({
        name: props.recipe ? props.recipe.name : '',
        ingredients: props.recipe ? props.recipe.ingredients : [],
    })

    const createBlankIngredient = () => {
        return {
            num: 1,
            denom: 1,
            name: '',
            unit: null
    }};

    return (
        <div className="popup-outer">
            <div className="recipe-editor">
                <h1>New Recipe</h1>
                <div className="recipe-editor-form">
                    {*/ /* <input type="text" value={recipe.name} onChange={(ev) => setRecipe({name: ev.target.value})}/> */ /*}
                    <CssTextField label="Name" variant="outlined" style={{backgroundColor: "white"}}/>
                </div>
                {*/ /* <div className="recipe-editor-details">
                    {props.recipe.ingredients.map(i => 
                        <p key={i.id} style={{textTransform: "capitalize"}}>
                            {strAssembly(i)}
                        </p>)}
                    <p>
                        {props.recipe.notes}
                    </p>
                </div> */ /*}
            </div>
        </div>
    );
}

export default RecipeEditor;*/