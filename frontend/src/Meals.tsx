import { Button, CircularProgress } from '@material-ui/core';
import './Meals.scss';
import useTrigger from 'react-use-trigger/useTrigger';
import createTrigger from 'react-use-trigger';
import { useFetchAPI } from './util/fetchAPI';
import { MutableRefObject, useEffect, useMemo, useReducer, useRef, useState } from 'react';
import MealEntry from './components/MealEntry';
import { useFetchControlAPI } from './util/fetchAPI2';
import { MealNewDayPopup } from './components/Form';
import { Dayjs } from 'dayjs';
import { useSnackbar } from './components/Snackbar';


const updateMealsTrigger = createTrigger();


interface IGroupedMeals {
    [index: string]: IMeal[];
}

function breakUpByDate(meals?: IMeal[]): IGroupedMeals | null {
    if (!meals) { return null };
    const out: IGroupedMeals = {};
    for (let meal of meals) {
        if (!(meal.day in out)) {
            out[meal.day] = [];
        }
        out[meal.day].push(meal);
    }
    return out;
}


function getClosestDay(grouped_meals?: IGroupedMeals): string | null {
    if (!grouped_meals) { return null; }
    const arr = Object.keys(grouped_meals);
    const now = Date.now();

    let closest: string | null = null;
    let dis: number = Infinity;
    for (let day of arr) {
        let thisDis = Math.abs(Date.parse(day) - now);
        if (thisDis < dis) {
            dis = thisDis;
            closest = day;
        }
    }
    return closest;
}

export interface IRecipeData {
    [index: number]: string
}

export interface IMeal {
    id: number,
    label: string,
    recipe_id: number,
    user_id: number,
    day: string
}

interface IState {
    data: IGroupedMeals,
    updated: number[]
}

function setPush(id: number, arr: number[]): number[] {
    if (arr.indexOf(id) === -1) {
        return [...arr, id];
    }
    else {
        return [...arr];
    }
}

function setPushLots(ids: number[], arr: number[]): number[] {
    return [...arr, ...ids.filter(x => arr.indexOf(x) === -1)];
}


export interface IAction {
    type: 'overwrite' | 'set-recipe' | 'set-label' | 'set-day' | null,
    data: any,
    day?: string,
    id?: number
}

function reduceState(state: IState | null, action: IAction) {
    if (action.type === 'overwrite') {
        // console.log('all meals set:', action.data);
        return {data: action.data, updated: []};
    }
    // if (typeof action.text !== 'string') {
    //     throw new TypeError(`SnackBar: Expected string for text, but got ${action.text}`)
    // }
    // const clean = {type: action.type, text: action.text};
    
    if (state === null) {
        throw new TypeError('Meals: Cannot alter state when state is null');
    }

    // console.log('Got action:', action);

    switch (action.type) {
        case 'set-recipe':
            let newState = {...state.data};
            if (action.day && action.id) {
                for (let meal of newState[action.day]) {
                    if (meal.id === action.id) {
                        meal.recipe_id = action.data;
                        break;
                    }
                }
            }
            else {
                throw new TypeError('Meals: Expected key day and id');
            }

            return {data: newState, updated: setPush(action.id, state.updated)};
        case 'set-label':
            let newState2 = {...state.data};
            if (action.day && action.id) {
                for (let meal of newState2[action.day]) {
                    if (meal.id === action.id) {
                        meal.label = action.data;
                        break;
                    }
                }
            }
            else {
                throw new TypeError('Meals: Expected key day');
            }

            return {data: newState2, updated: setPush(action.id, state.updated)};
        case 'set-day':
            let newState3 = {...state.data};
            let ids = [];
            if (action.day) {
                const tmp = newState3[action.day];
                delete newState3[action.day];
                newState3[action.data] = tmp;
                ids = tmp.map(e => e.id);
            }
            else {
                throw new TypeError('Meals: Expected key day');
            }
            return {data: newState3, updated: setPushLots(ids, state.updated)};;
        case null:
            return state;
        default:
            throw new TypeError(`Meals: Unexpected value for type, got ${action.type}`);
    }
}


export default function Meals() {
    const updateMealsTriggerValue = useTrigger(updateMealsTrigger);
    const [ isLoading, mealsData_raw ] = useFetchAPI('meal', [updateMealsTriggerValue] as any);
    const [ isLoading2, recipesData_raw ] = useFetchAPI('recipe?minimum=True', [updateMealsTriggerValue] as any);

    const recipesData = useMemo(() => {
        const obj: IRecipeData = {};
        if (!recipesData_raw) { return null; }
        for (let recipe of recipesData_raw) {
            obj[recipe.id] = recipe.name;
        }
        return obj;
    }, [recipesData_raw]);

    const snackbar = useSnackbar();

    const [mealsStateAll, dispatch]: [IState, (a: IAction) => void] = useReducer(reduceState, {data: null, updated: []});
    const mealsState = mealsStateAll.data;

    const sendMealPlan = useFetchControlAPI('meal', 'PUT', data => {});
    const addMealPlan = useFetchControlAPI('meal', 'POST', data => {
        updateMealsTrigger();
    });

    const addMealPlanDay = (day: string) => {
        addMealPlan(JSON.stringify({day: day}));
    }

    const sendDB = () => {
        //sendMealPlan();
        const needToFlatten = Object.entries(mealsState).map(([day, arr]) => arr.filter(m => mealsStateAll.updated.indexOf(m.id) !== -1));
        const flat = needToFlatten.reduce((prev, elem) => prev.concat(elem));
        if (flat.length === 0) {
            return;
        }
        sendMealPlan(JSON.stringify(flat));
    };


    // whenever data from db is refreshed, overwrite the state
    useEffect(() => {
        const groupedMeals = breakUpByDate(mealsData_raw);
        dispatch({type: 'overwrite', data: groupedMeals})
    }, [mealsData_raw]);

    const ready = useMemo(() => (!isLoading && !isLoading2 && mealsState && recipesData), [isLoading, isLoading2, mealsState, recipesData]);

    // for auto-scrolling to closestDay
    const closestDay = useMemo(() => getClosestDay(mealsState), [mealsState]);
    const closestDayRef: MutableRefObject<HTMLDivElement | null> = useRef(null);

    useEffect(() => {
        // item.scrollIntoView({
        //     behavior: 'smooth',
        //     block: 'start'
        // });   
        // console.log(closestDayRef.current);
        if (closestDayRef.current) {
            closestDayRef.current.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            }); // might be problematic and require checks so it only runs once
        }
    }, [closestDay]);

    const [showNew, setShowNew] = useState(false);

    return (
    <div className="frame meal-main">
        <div className="header">
            <h1>
                Meal Planner
            </h1>
            <div className="actions">
                <Button className="actions-buttons" onClick={() => console.log('search')}>
                    <i className="fas fa-search" style={{color: 'black'}}></i>
                </Button>
                <Button className="actions-buttons" onClick={() => {
                    setShowNew(true);
                }}>
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
            {!ready ? 
                <CircularProgress className="circular-progress"/>
            : 
            Object.entries(mealsState).map(([date, meals]) =>
                <MealEntry 
                    key={date} 
                    date={date} 
                    meals={meals} 
                    closestDay={closestDay} 
                    closestDayRef={closestDayRef} 
                    recipesData={recipesData}
                    dispatch={dispatch}
                    updateDB={sendDB}
                    addMealPlanDay={addMealPlanDay}
                    />
            )}
        </div>

        <MealNewDayPopup
            show={showNew}
            callback={(data: Dayjs) => {
                const s = data.format('YYYY-MM-DD');

                if (s in mealsState) {
                    snackbar({type: 'warning', text: 'Meal plan for day already exists'});
                    return;
                }

                addMealPlanDay(s);
            }
            } 
            handleClose={() => setShowNew(false) }
        />
    </div>
    )
}