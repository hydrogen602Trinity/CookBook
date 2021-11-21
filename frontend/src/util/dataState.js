import useBetterState from "./classLikeState";
import { convertFraToStr, isInteger } from "./util";
import { AuthError, fetchControlAPI, fullPath } from "./fetchAPI";
import { useState } from "react";
import { Ingredient, serialize_ingredient } from "./dataTypes";
import { useNavigate } from "react-router";
import { useSnackbar } from "../components/Snackbar";


export function useRecipe(recipe) {
    const dispatchMsg = useSnackbar();
    const nav = useNavigate();
    const sendToLogin = () => {
        dispatchMsg({type: 'error', text: 'Authentication Required'});
        nav('/');
    };

    recipe = {
        name: '',
        notes: '',
        ...recipe,
        ingredients: (recipe && recipe.ingredients) ? recipe.ingredients.map(i => new Ingredient(i)) : [],
    };

    const [state, setState] = useBetterState(recipe);
    const [error, setError] = useState(null);

    function setIngredient(idx, ingredient) {
        idx = parseInt(idx);
        setState(prevRecipe => {
            const newIngredients = prevRecipe.ingredients.map((e,i) => {
                if (idx === i) {
                    return {...e, ...ingredient};
                }
                return e;
            });
            return {ingredients: newIngredients};
        });
    }

    const ingredients_handler = {
        get(_, prop) {
            if (!isInteger(prop)) {
                return state.ingredients[prop];
            }
            else {
                const idx = prop;
                const i = state.ingredients[idx];
                return {
                    get id() {
                        return i.id;
                    },
                    get name() {
                        return i.name;
                    },
                    set name(prop) {
                        setIngredient(idx, {name: prop});
                    },
                    get amount() {
                        return i.amount;
                    },
                    set amount(prop) {
                        setIngredient(idx, {amount: prop, temp_amount: convertFraToStr(prop)});
                    },
                    get temp_amount() {
                        return i.temp_amount;
                    },
                    set temp_amount(prop) {
                        setIngredient(idx, {temp_amount: prop});
                    },
                    get unit() {
                        return i.unit;
                    },
                    set unit(prop) {
                        setIngredient(idx, {unit: prop});
                    }
                };
            }
        },
        set(_, idx, ingredient) {
            if (!isInteger(idx)) {
                throw new Error('Expected int');
            }
            setIngredient(idx, ingredient);
        }
    };

    const proxy = new Proxy(state.ingredients, ingredients_handler);

    function generateDataToSend() {
        return {
            ...state,
            ingredients: state.ingredients.filter(i => i.name.length > 0)
            .map(i => serialize_ingredient(i))
        };
    }

    const obj = {
        get id() {
            return state.id;
        },
        get name() {
            return state.name;
        },
        set name(prop) {
            setState({name: prop});
        },
        get notes() {
            return state.notes;
        },
        set notes(prop) {
            setState({notes: prop});
        },
        get ingredients() {
            return proxy;
        },
        newIngredient() {
            setState(prevState => {
                return {
                    ingredients: [...prevState.ingredients, new Ingredient()]
                };
            });
        },
        async refreshRecipe(tmp_id) {
            const id = isInteger(tmp_id) ? tmp_id : state.id;
            if (!isInteger(id)) {
                throw new Error('Recipe id invalid: ' + id);
            }
            let data = null;
            try {
                const response = await fetch(fullPath('recipe/' + id));
                data = await response.json();
            }
            catch (err) {
                console.error('refreshRecipe', err);
                setError(err + '');
                throw err;
            }

            const ingredients = data.ingredients.map(i => new Ingredient(i));
            setState({
                ...data,
                ingredients: ingredients
            });
            return data;
        },
        async sendRecipe() {
            const data = generateDataToSend();
            setState(prevState => {
                return {
                    ingredients: prevState.ingredients.filter(i => i.name.length > 0)
                };
            });
            console.log('sending data:', data, state.ingredients);
            let result = null;
            try {
                result = await fetchControlAPI('recipe', 'PUT', data);
                if (!isInteger(result)) {
                    throw new Error('Expected PUT /recipe to return int, but got ' + result);
                }
                setState({
                    id: parseInt(result)
                });
                await this.refreshRecipe(result);
            }
            catch (err) {
                if (err instanceof AuthError) {
                    sendToLogin();
                    return null;
                }
                console.error('sendRecipe', err);
                setError(err + '');
                throw err;
            }
            
            console.log('response', result);
            return result;
        },
        async deleteThis() {
            let result = null;
            if (isInteger(state.id)) {
                console.log('deleting...');
                try {
                    result = await fetchControlAPI('recipe/' + state.id, 'DELETE', null, false);
                    console.log('deleted');
                    setState({
                        name: '',
                        notes: '',
                        ingredients: [],
                    });
                }
                catch (err) {
                    if (err instanceof AuthError) {
                        sendToLogin();
                        return null;
                    }
                    console.error('deleteThis', err);
                    setError(err + '');
                    throw err;
                }
            }
            return result;
        },
        get error() {
            return error;
        }
    }

    return obj;
}