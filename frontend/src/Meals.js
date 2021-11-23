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

function TimelineItemWrap(props) {
    return (
    <TimelineItem>
        <TimelineSeparator>
            <TimelineDot color="primary" variant={props.variant ? props.variant : 'filled'}/>
            <TimelineConnector />
        </TimelineSeparator>
        <TimelineContent>{props.children}</TimelineContent>
    </TimelineItem>
    )
}


export default function Meals() {
    const isLoading = false;
    const meals = [
        {id: 0, day: '2021-10-01'}, 
        {id: 1, day: '2021-10-02'}, 
        {id: 2, day: '2021-10-02'}];

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
            <div className="container">
            <Timeline>
            <TransitionGroup>
                <Collapse key={'date'} >
                    <TimelineItemWrap variant="outlined">{'2021-10-02'}</TimelineItemWrap>
                </Collapse>
                {meals.map((meal, i) => 
                    <Collapse key={meal.id} >
                        <TimelineItemWrap>{JSON.stringify(meal)}</TimelineItemWrap>
                    </Collapse>)}
            </TransitionGroup>
            </Timeline>
            </div>
            }
        </div>
    </div>
    )
}