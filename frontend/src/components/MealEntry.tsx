import { IconButton } from "@mui/material";
import { MutableRefObject, useState, ReactNode } from "react";
import { IRecipeData, IMeal, IAction } from "../Meals";
import Collapse from '@mui/material/Collapse';
import EditIcon from '@material-ui/icons/Edit';
import SaveIcon from '@material-ui/icons/Save';
import NativeSelect from '@mui/material/NativeSelect';
import { TransitionGroup } from 'react-transition-group';
import Timeline from '@mui/lab/Timeline';
import TimelineItem from '@mui/lab/TimelineItem';
import TimelineSeparator from '@mui/lab/TimelineSeparator';
import TimelineConnector from '@mui/lab/TimelineConnector';
import TimelineContent from '@mui/lab/TimelineContent';
import TimelineDot from '@mui/lab/TimelineDot';
import { Button } from "@material-ui/core";
import "./MealEntry.scss";


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


export interface IEntryProps {
    recipesData: IRecipeData | null,
    date: string,
    closestDay: string | null,
    closestDayRef: MutableRefObject<HTMLDivElement | null>,
    meals: IMeal[],
    dispatch: (a: IAction) => void,
    updateDB: () => void,
    addMealPlanDay: (day: string) => void
}

function convertDate(s: string): string {
    const tmp = (new Date(s)).toUTCString();
    return tmp.substring(0, tmp.length-13);
}

export default function MealEntry(props: IEntryProps) {
    const [edit, setEdit] = useState(false);


    const recipesData: IRecipeData = (props.recipesData === null) ? 
        (() => { throw new TypeError('Data not ready yet in MealEntry'); })() : props.recipesData;

    const meal_types = ['Breakfast', '2nd Breakfast', 'Brunch', 'Lunch', 'Dinner', 'Other'];
    // console.log(props.recipesData)
    return (
    <div className="container meal-entry" ref={props.date === props.closestDay ? props.closestDayRef : undefined}>
        <IconButton className="icon-button" onClick={() => {
            if (edit) {
                props.updateDB();
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
                    {/* && !edit is because another tag is added below, so none of these are last */}
                    <TimelineItemWrap last={i + 1 === props.meals.length && !edit}>
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
            { edit ? <Collapse key={'new'}>
                <TimelineItemWrap last={true}>
                    <p>Add Meal</p>
                    <Button className="actions-buttons" onClick={() => {
                        // add
                        props.addMealPlanDay(props.date);
                    }}>
                        <i className="fas fa-plus" style={{color: 'black'}}></i>
                    </Button>
                </TimelineItemWrap>
            </Collapse> : null }
        </TransitionGroup>
        </Timeline>
    </div>
    );
}