import Timeline from '@mui/lab/Timeline';
import TimelineItem from '@mui/lab/TimelineItem';
import TimelineSeparator from '@mui/lab/TimelineSeparator';
import TimelineConnector from '@mui/lab/TimelineConnector';
import TimelineContent from '@mui/lab/TimelineContent';
import TimelineDot from '@mui/lab/TimelineDot';
import Collapse from '@mui/material/Collapse';
import EditIcon from '@material-ui/icons/Edit';
import SaveIcon from '@material-ui/icons/Save';
import NativeSelect from '@mui/material/NativeSelect';



import { Button, CircularProgress, IconButton } from '@material-ui/core';
import { TransitionGroup } from 'react-transition-group';
import './Meals.scss';
import useTrigger from 'react-use-trigger/useTrigger';
import createTrigger from 'react-use-trigger';
import { useFetchAPI } from './util/fetchAPI';
import { MutableRefObject, ReactNode, useEffect, useMemo, useReducer, useRef, useState } from 'react';


interface TimeIProps {
    variant?: "filled" | "outlined",
    last?: boolean,
    children: ReactNode
}

function TimelineItemWrap(props: TimeIProps) {
    return (
    <TimelineItem>
        <TimelineSeparator>
            <TimelineDot color="primary" variant={props.variant ? props.variant : 'filled'}/>
            { props.last ? null : <TimelineConnector />}
        </TimelineSeparator>
        <TimelineContent>{props.children}</TimelineContent>
    </TimelineItem>
    )
}

const updateMealsTrigger = createTrigger();


function convertDate(s: string): string {
    const tmp = (new Date(s)).toUTCString();
    return tmp.substring(0, tmp.length-13);
}

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

    // // these are sorted so binary search

    // let start = 0;
    // let end = arr.length;
    // let i = parseInt((end - start) / 2);
    // while (true) {

    // }
}

interface IRecipeData {
    [index: number]: string
}

interface IMeal {
    id: number,
    label: string,
    recipe_id: number,
    user_id: number,
    day: string
}

interface IEntryProps {
    recipesData: IRecipeData | null,
    date: string,
    closestDay: string | null,
    closestDayRef: MutableRefObject<HTMLDivElement | null>,
    meals: IMeal[],
    dispatch: (a: IAction) => void
}

function MealEntry(props: IEntryProps) {
    const [edit, setEdit] = useState(false);

    const recipesData: IRecipeData = (props.recipesData === null) ? 
        (() => { throw new TypeError('Data not ready yet in MealEntry'); })() : props.recipesData;

    const meal_types = ['Breakfast', '2nd Breakfast', 'Brunch', 'Lunch', 'Dinner', 'Other'];
    // console.log(props.recipesData)
    return (
    <div className="container" ref={props.date === props.closestDay ? props.closestDayRef : undefined}>
        <IconButton className="icon-button" onClick={() => {
            if (edit) {
                console.log('TODO: Send info to db');
            }
            setEdit(!edit);
        }}>
            {edit ?
                <SaveIcon className="icon-small" />
            :
                <EditIcon className="icon-small" />
            }
        </IconButton>
        <Timeline>
        <TransitionGroup>
            <Collapse key={props.date}>
                <TimelineItemWrap variant="outlined">{convertDate(props.date)}</TimelineItemWrap>
            </Collapse>
            {props.meals.map((meal, i) => 
                <Collapse key={meal.id} >
                    <TimelineItemWrap last={i + 1 === props.meals.length}>
                        {edit ? 
                        <>
                            <NativeSelect
                                value={meal.label}
                                onChange={ev => {
                                    props.dispatch({type: 'set-label', day: props.date, data: ev.target.value, id: meal.id})
                                }}
                                fullWidth
                                >
                                {meal_types.map(e => <option key={e} value={e}>{e}</option>)}
                            </NativeSelect>
                            <NativeSelect
                                value={meal.recipe_id}
                                onChange={ev => {
                                    props.dispatch({type: 'set-recipe', day: props.date, data: ev.target.value, id: meal.id})
                                }}
                                fullWidth
                                >
                                {Object.entries(recipesData).map(([id, name]) => <option key={id} value={id}>{name}</option>)}
                            </NativeSelect>
                        </>
                        : <>
                            <p>{meal.label}</p>
                            <p>{recipesData[meal.recipe_id]}</p>
                        </> }
                        
                    </TimelineItemWrap>
                </Collapse>)}
        </TransitionGroup>
        </Timeline>
    </div>
    );
}

interface IAction {
    type: 'overwrite' | 'set-recipe' | 'set-label' | 'set-day' | null,
    data: any,
    day?: string,
    id?: number
}

function reduceState(state: IGroupedMeals | null, action: IAction) {
    if (action.type === 'overwrite') {
        // console.log('all meals set:', action.data);
        return action.data;
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
            let newState = {...state};
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
            return newState;
        case 'set-label':
            let newState2 = {...state};
            if (action.day) {
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
            return newState2;
        case 'set-day':
            let newState3 = {...state};
            if (action.day) {
                const tmp = newState3[action.day];
                delete newState3[action.day];
                newState3[action.data] = tmp;
            }
            else {
                throw new TypeError('Meals: Expected key day');
            }
            return newState3;
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

    const [mealsState, dispatch]: [IGroupedMeals, (a: IAction) => void] = useReducer(reduceState, null);

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
                <Button className="actions-buttons" onClick={() => console.log('add')}>
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
                    />
            )}
        </div>
    </div>
    )
}