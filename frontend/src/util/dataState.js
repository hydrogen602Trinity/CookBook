import useBetterState from "./classLikeState";
import Fraction from "fraction.js";
import { convertFraToStr } from "./util";
import { fullPath } from "./fetchAPI";
import { useState } from "react";


export function useRecipe(recipe) {
    recipe = {
        name: '',
        notes: '',
        ingredients: [],
        ...recipe
    };

    function Ingredient() {
        this.name = '';
        this.amount = new Fraction(1);
        this.temp_amount = '1';
        this.unit = '';
    }

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
            if (parseInt(prop) + '' === 'NaN') {
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
            if (parseInt(prop) + '' === 'NaN') {
                throw new Error('Expected int');
            }
            setIngredient(idx, ingredient);
        }
    };

    const proxy = new Proxy(state.ingredients, ingredients_handler);

    function generateDataToSend() {
        return {
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
        // mapIngredients(func) {
        //     if (typeof func !== 'function') {
        //         throw new Error('Expected function');
        //     }
        //     return state.ingredients.map(func);
        // },
        newIngredient() {
            setState(prevState => {
                return {
                    ingredients: [...prevState.ingredients, new Ingredient()]
                };
            });
        },
        async refreshRecipe() {
            let data = null;
            try {
                const response = await fetch(fullPath('recipe/' + recipe.id));
                data = await response.json();
            }
            catch (err) {
                console.error(err);
                setError(err + '');
                throw err;
            }

            const ingredients = data.ingredients.map(i => {
                const newIngredient = {...i};
                newIngredient.amount = new Fraction(i.num, i.denom);
                newIngredient.temp_amount = convertFraToStr(newIngredient.amount);
                delete newIngredient.num;
                delete newIngredient.denom;
                return newIngredient;
            });
            setState({
                ...data,
                ingredients: ingredients
            });
        },
        async sendRecipe(callback) {
            const data = generateDataToSend();
            console.log(data);
            let result = null;
            try {
                result = await fetchControlAPI('recipe', 'PUT', data);
            }
            catch (err) {
                console.error(err);
                setError(err + '');
                throw err;
            }
            
            console.log('response', result);
            if (callback) {
                callback(result);
            } 
        },
        get error() {
            return error;
        }
    }

    return obj;
}