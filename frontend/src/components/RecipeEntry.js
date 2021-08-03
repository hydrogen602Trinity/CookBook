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

    const [recipe, setRecipe] = useBetterState({
        ...props.recipe,
        ingredients: props.recipe.ingredients.map(i => {
            const newIngredient = {...i};
            newIngredient.amount = new Fraction(i.num, i.denom);
            newIngredient.temp_amount = convertFraToStr(newIngredient.amount);
            delete newIngredient.num;
            delete newIngredient.denom;
            return newIngredient;
        })
    });
    // const recipe = useRecipe(props.recipe);

    function generateDataToSend() {
        return {//ingredients: prevRecipe.ingredients
            ...recipe,
            ingredients: recipe.ingredients.filter(i => i.name.length > 0)
            .map(i => {
                const newIngredient = {...i};
                newIngredient.num = i.amount.n * i.amount.s;
                newIngredient.denom = i.amount.d;
                delete newIngredient.amount;
                delete newIngredient.temp_amount;
                return newIngredient;
            })
        };
    }

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

        function onChange(ev) {
            setRecipe(prevRecipe => {
                const newIngredients = prevRecipe.ingredients.map((e,i) => {
                    if (index === i) {
                        e.name = ev.target.value;
                    }
                    return e;
                });
                return {ingredients: newIngredients};
            });
        };

        function onChangeAmount(ev) {
            setRecipe(prevRecipe => {
                const newIngredients = prevRecipe.ingredients.map((e,i) => {
                    if (index === i) {
                        e.temp_amount = ev.target.value;
                    }
                    return e;
                });
                return {ingredients: newIngredients};
            });
        };

        function onBlurAmount() {
            const value = recipe.ingredients[index].temp_amount;
            try {
                const f = new Fraction(value);
                setRecipe(prevRecipe => {
                    const newIngredients = prevRecipe.ingredients.map((e,i) => {
                        if (index === i) {
                            e.amount = f;
                            e.temp_amount = convertFraToStr(f);
                        }
                        return e;
                    });
                    return {ingredients: newIngredients};
                });
            } catch (e) { 
                if (e instanceof Fraction.InvalidParameter) {
                    console.log('Invalid fraction entered: ' + value);
                }
                else {
                    throw e;
                }
            } 
        }

        function onSelectChange(ev) {
            setRecipe(prevRecipe => {
                const newIngredients = prevRecipe.ingredients.map((e,i) => {
                    if (index === i) {
                        e.unit = ev.target.value;
                    }
                    return e;
                });
                return {ingredients: newIngredients};
            });
        }

        return (
            <div className="recipe-ingredient" key={index}>
                {edit ? 
                    <input 
                        type="text" 
                        placeholder="Ingredient name"
                        value={i.name} 
                        onChange={onChange}/> 
                : 
                    <span>{i.name}</span>
                }
                {edit ?
                    <input 
                        type="text" 
                        value={i.temp_amount}
                        onChange={onChangeAmount}
                        onBlur={onBlurAmount}></input>
                :
                    <span>{convertFraToStr(i.amount)}</span>
                }
                {edit ? 
                    <select value={(i.unit === null) ? '' : i.unit} onChange={onSelectChange}>
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

    function addIngredient() {
        const newIngredient = {
            name: '',
            amount: new Fraction(1),
            temp_amount: '1',
            unit: '',
        }
        setRecipe(prevRecipe => {
            return {
                ingredients: [...prevRecipe.ingredients, newIngredient]
            };
        });
    }

    function sendData() {
        // const path = (recipe.id) ? `recipe/${recipe.id}` : 'recipe';
        const data = generateDataToSend();
        console.log(data);
        fetchControlAPI('recipe', 'PUT', data).then(data => {
            console.log('response', data);
            props.updateRecipesTrigger();
        }).catch(e =>
            console.log('error', e)
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
                    <IconButton onClick={addIngredient}>
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
                        <IconButton onClick={() => {
                            if (edit) {
                                // filter out empty name stuff
                                setRecipe(prevRecipe => {
                                    return {
                                        ingredients: prevRecipe.ingredients.filter(i => i.name.length > 0)
                                    };
                                });
                                sendData();
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