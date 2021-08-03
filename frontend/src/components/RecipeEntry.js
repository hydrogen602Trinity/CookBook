import { createRef, useLayoutEffect, useState } from "react";
import Fraction from "fraction.js";
import Collapse from '@material-ui/core/Collapse';
import './RecipeEntry.css'

import useBetterState from "../util/classLikeState";
import { IconButton } from "@material-ui/core";
import DeleteIcon from '@material-ui/icons/Delete';
import EditIcon from '@material-ui/icons/Edit';
import KeyboardArrowUpIcon from '@material-ui/icons/KeyboardArrowUp';
import SaveIcon from '@material-ui/icons/Save';
import AddCircleOutlineIcon from '@material-ui/icons/AddCircleOutline';
import { fetchAPI, fetchControlAPI } from "../util/fetchAPI";
import { convertFraToStr } from "../util/util";
import { useRecipe } from "../util/dataState";


function RecipeEntry(props) {
    const [isExpanded, setExpanded] = useState(false);

    const recipe = useRecipe(props.recipe);

    const units = [
        '',                 // no unit
        'kg', 'g', 'Pfund', // weight metric
        'l', 'ml',          // volume metric
        'cup',
        'tsp', 'tbsp',       // volume
        'pk'
    ]
    // optgroup for grouping units

    const [edit, setEdit] = useState(false);

    function expand() {
        if (!isExpanded) {
            setExpanded(true);
        }
    }

    function deleteThis() {
        if (recipe.id === undefined) {
            // not in db
            props.updateRecipesTrigger();
        }
        else {
            const f = (e) => console.error(e);
            fetchAPI('recipe/' + props.recipe.id, null, 'delete', (e) => {
                console.log('Success!', e);
                props.updateRecipesTrigger();
            }, f);
        }
    }

    const textAreaRef = createRef();
    useLayoutEffect(() => {
        if (edit && textAreaRef.current) {
            textAreaRef.current.style.height = "";
            textAreaRef.current.style.height = textAreaRef.current.scrollHeight +  "px";
        }
    }, [edit, textAreaRef]);

    function generateIngredientInput(index) {
        // not a react component but a helper func
        const i = recipe.ingredients[index];

        function onBlurAmount() {
            const value = i.temp_amount;
            try {
                const f = new Fraction(value);

                i.amount = f;
                i.temp_amount = convertFraToStr(f);
            } catch (e) { 
                if (e instanceof Fraction.InvalidParameter) {
                    console.log('Invalid fraction entered: ' + value);
                }
                else {
                    throw e;
                }
            } 
        }

        return (
            <div className="recipe-ingredient" key={index}>
                {edit ? 
                    <input 
                        type="text" 
                        placeholder="Ingredient name"
                        value={i.name} 
                        onChange={ev => i.name = ev.target.value}/> 
                : 
                    <span>{i.name}</span>
                }
                {edit ?
                    <input 
                        type="text" 
                        value={i.temp_amount}
                        onChange={ev => i.temp_amount = ev.target.value}
                        onBlur={onBlurAmount}></input>
                :
                    <span>{convertFraToStr(i.amount)}</span>
                }
                {edit ? 
                    <select value={(i.unit === null) ? '' : i.unit} onChange={ev => i.unit = ev.target.value}>
                    {
                        units.map((u, i) => 
                            <option value={u} key={i}>{u}</option>)
                    }
                    </select>
                :
                    <span style={{textTransform: 'none'}}>{i.unit}</span>
                }
                
            </div>
        );
        
    }

    return (
        <div onClick={expand} is-expanded={isExpanded ? '' : undefined} className="recipe-entry">
            <div className="recipe-field">
                {edit ? 
                    <input type="text" value={recipe.name} onChange={(ev) => recipe.name = ev.target.value}></input>
                : 
                    <span>{recipe.name}</span>
                }
            </div>
            <Collapse 
                in={isExpanded} 
                timeout={200} 
                unmountOnExit>
                <div className="recipe-details">
                    {recipe.ingredients.map((_,i) => 
                        generateIngredientInput(i)
                    )}
                    { edit ? 
                    <IconButton onClick={recipe.newIngredient}>
                        <AddCircleOutlineIcon className="recipe-icon-small" />
                    </IconButton> : null }
                    { edit ? 
                    <textarea 
                        className="recipe-notes"
                        ref={textAreaRef}
                        maxLength={4096}
                        value={recipe.notes} 
                        onChange={
                            (ev) => {
                                recipe.notes = ev.target.value;
                                ev.target.style.height = "";
                                ev.target.style.height = ev.target.scrollHeight +  "px";
                            }
                        }>    
                    </textarea>
                    :
                    <p className="recipe-notes">
                        {recipe.notes}
                    </p>
                    }
                    
                    <div className="recipe-menu">
                        <IconButton onClick={deleteThis}>
                            <DeleteIcon className="recipe-icon" />
                        </IconButton>
                        <IconButton onClick={() => {
                            setExpanded(false);
                            setEdit(false);
                        }}>
                            <KeyboardArrowUpIcon className="recipe-icon" />
                        </IconButton>
                        <IconButton onClick={() => {
                            if (edit) {
                                recipe.sendRecipe().then(data => {
                                    console.log('response', data);
                                }).catch(e =>
                                    console.log('error', e)
                                );
                            }
                            setEdit(!edit);
                        }}>
                            {edit ?
                                <SaveIcon className="recipe-icon" />
                            :
                                <EditIcon className="recipe-icon" />
                            }
                        </IconButton>
                    </div>
                </div>
            </Collapse>
        </div>
    );
}

export default RecipeEntry;