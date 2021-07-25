import { createRef, useLayoutEffect, useState } from "react";
import Collapse from '@material-ui/core/Collapse';
import './RecipeEntry.css'

import useBetterState from "../util/classLikeState";
import { IconButton } from "@material-ui/core";
import DeleteIcon from '@material-ui/icons/Delete';
import EditIcon from '@material-ui/icons/Edit';
import KeyboardArrowUpIcon from '@material-ui/icons/KeyboardArrowUp';
import { fetchAPI } from "../util/fetchAPI";


function RecipeEntry(props) {
    const [isExpanded, setExpanded] = useState(false);

    const [recipe, setRecipe] = useBetterState({
        ...props.recipe
    });

    const [edit, setEdit] = useState(false);

    function expand() {
        if (!isExpanded) {
            setExpanded(true);
        }
    }

    function deleteThis() {
        const f = (e) => console.error(e);
        fetchAPI('recipe/' + props.recipe.id, null, 'delete', (e) => {
            console.log('Success!', e);
            props.updateRecipesTrigger();
        }, f);
    }

    const textAreaRef = createRef();
    useLayoutEffect(() => {
        if (edit && textAreaRef.current) {
            textAreaRef.current.style.height = "";
            textAreaRef.current.style.height = textAreaRef.current.scrollHeight +  "px";
            console.log('yeet');
        }
    }, [edit]);

    function generateIngredientInput(index) {
        // not a react component but a helper func
        const i = recipe.ingredients[index];

        function onChange(ev) {
            setRecipe(prevRecipe => {
                const newIngredients = prevRecipe.ingredients.map((e,i) => {
                    if (index === i) {
                        e.name = ev.target.value;
                    }
                    return e;
                });
                return newIngredients;
            })
        };

        return (
            <p className="recipe-ingredient" key={i.id}>
                {edit ? 
                    <input type="text" value={i.name} onChange={onChange}/> 
                : 
                    <span>{i.name}</span>
                }
                <span>{`${i.num}${i.denom > 1 ? '/'+i.denom : ''}`}</span>
                <span>{i.unit}</span>
            </p>
        );
        
    }

    return (
        <div onClick={expand} is-expanded={isExpanded ? '' : undefined} className="recipe-entry">
            <div className="recipe-field">
                {edit ? 
                    <input type="text" value={recipe.name} onChange={(ev) => setRecipe({name: ev.target.value})}></input>
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
                    <textarea 
                        className="recipe-notes"
                        ref={textAreaRef}
                        maxLength={4096}
                        value={recipe.notes} 
                        onChange={
                            (ev) => {
                                setRecipe({notes: ev.target.value});
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
                        <IconButton onClick={() => setEdit(true)}>
                            <EditIcon className="recipe-icon" />
                        </IconButton>
                    </div>
                </div>
            </Collapse>
        </div>
    );
}

export default RecipeEntry;