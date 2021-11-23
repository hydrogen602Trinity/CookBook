import Timeline from '@mui/lab/Timeline';
import TimelineItem from '@mui/lab/TimelineItem';
import TimelineSeparator from '@mui/lab/TimelineSeparator';
import TimelineConnector from '@mui/lab/TimelineConnector';
import TimelineContent from '@mui/lab/TimelineContent';
import TimelineDot from '@mui/lab/TimelineDot';
import Collapse from '@mui/material/Collapse';

import { Button, CircularProgress } from '@material-ui/core';
import { TransitionGroup } from 'react-transition-group';
import './Meals.scss';
import useTrigger from 'react-use-trigger/useTrigger';
import createTrigger from 'react-use-trigger';
import { useFetchAPI } from './util/fetchAPI';
import { useMemo } from 'react';

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


export default function Meals() {
    const updateMealsTriggerValue = useTrigger(updateMealsTrigger);
    const [ isLoading, mealsData, error ] = useFetchAPI('meal', [updateMealsTriggerValue]);

    const groupedMeals = useMemo(() => breakUpByDate(mealsData), [mealsData]);

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
            {isLoading ? 
                <CircularProgress className="circular-progress"/>
            : 
            Object.entries(groupedMeals).map(([date, meals]) =>
                <div className="container" key={date}>
                <Timeline>
                <TransitionGroup>
                    <Collapse key={date}>
                        <TimelineItemWrap variant="outlined">{convertDate('2021-10-02')}</TimelineItemWrap>
                    </Collapse>
                    {meals.map((meal, i) => 
                        <Collapse key={meal.id} >
                            <TimelineItemWrap last={i + 1 === meals.length}>
                                <p>{meal.label}</p>
                                <p>{meal.recipe_name}</p>
                            </TimelineItemWrap>
                        </Collapse>)}
                </TransitionGroup>
                </Timeline>
                </div>
            )}
        </div>
    </div>
    )
}