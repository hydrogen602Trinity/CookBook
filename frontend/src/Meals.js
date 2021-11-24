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
import { useEffect, useMemo, useReducer, useRef, useState } from 'react';

function TimelineItemWrap(props) {
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


function convertDate(s) {
    const tmp = new Date(s).toGMTString();
    return tmp.substring(0, tmp.length-13);
}


function breakUpByDate(meals) {
    if (!meals) { return {} };
    const out = {};
    for (let meal of meals) {
        if (!(meal.day in out)) {
            out[meal.day] = [];
        }
        out[meal.day].push(meal);
    }
    return out;
}


function getClosestDay(grouped_meals) {
    const arr = Object.keys(grouped_meals);
    const now = Date.now();

    let closest = null;
    let dis = Infinity;
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


function MealEntry(props) {
    const [edit, setEdit] = useState(false);

    const meal_types = ['Breakfast', '2nd Breakfast', 'Brunch', 'Lunch', 'Dinner', 'Other'];
    
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
                                defaultValue={meal_types[0]}
                                fullWidth
                                >
                                {meal_types.map(e => <option key={e} value={e}>{e}</option>)}
                            </NativeSelect>
                            <NativeSelect
                                defaultValue={props.recipesData[0].id}
                                fullWidth
                                >
                                {props.recipesData.map(e => <option key={e.id} value={e.id}>{e.name}</option>)}
                            </NativeSelect>
                        </>
                        : <>
                            <p>{meal.label}</p>
                            <p>{meal.recipe_name}</p>
                        </> }
                        
                    </TimelineItemWrap>
                </Collapse>)}
        </TransitionGroup>
        </Timeline>
    </div>
    );
}


function reduceState(state, action) {
    // if (typeof action.text !== 'string') {
    //     throw new TypeError(`SnackBar: Expected string for text, but got ${action.text}`)
    // }
    // const clean = {type: action.type, text: action.text};

    switch (action.type) {
        case 'overwrite':
            return action.data;
        case 'set-recipe':
            for (let meal of state[action.day]) {
                if (meal.id === action.id) {
                    meal.recipe_id = action.recipe_id;
                    break;
                }
            }
            return state;
        case 'set-day':
            const data = state[action.day];
            delete state[action.day];
            state[action.newDay] = data;
        case null:
            return state;
        default:
            throw new TypeError(`Meals: Unexpected value for type, got ${action.type}`);
    }
}


export default function Meals() {
    const updateMealsTriggerValue = useTrigger(updateMealsTrigger);
    const [ isLoading, mealsData ] = useFetchAPI('meal', [updateMealsTriggerValue]);
    const [ isLoading2, recipesData_raw ] = useFetchAPI('recipe?minimum=True', [updateMealsTriggerValue]);

    const recipesData = useMemo(() => {
        const obj = {};
        for (let recipe of recipesData_raw) {
            obj[recipe.id] = recipe.name;
        }
        return obj;
    }, [recipesData_raw]);

    const [groupedMeals, closestDay] = useMemo(() => {
        const groupedMeals = breakUpByDate(mealsData);
        const closestDay = getClosestDay(groupedMeals);
        return [groupedMeals, closestDay];
    }, [mealsData]);

    const closestDayRef = useRef(null);

    const [mealsState, dispatch] = useReducer(reduceState, groupedMeals);
    useEffect(() => dispatch({type: 'overwrite', data: groupedMeals}), [groupedMeals]);

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
            {isLoading || isLoading2 ? 
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
                    reduceState={reduceState}
                    />
            )}
        </div>
    </div>
    )
}