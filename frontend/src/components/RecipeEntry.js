import { useState } from "react";
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

    const [state, setState] = useBetterState({
        editTitle: false,
        title: props.recipe.name
    });

    function strAssembly(i) {
        return `${i.name}: ${i.num}${i.denom > 1 ? '/'+i.denom : ''}${i.unit ? ' '+i.unit : ''}`
    }

    console.log(state);

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

    return (
        <div onClick={expand} is-expanded={isExpanded ? '' : undefined} className="recipe-entry">
            <div>
                {state.editTitle ? 
                    <input value={state.title} onChange={(ev) => setState({title: ev.target.value})}></input>
                : 
                    <span>{state.title}</span>
                }
            </div>
            <Collapse 
                in={isExpanded} 
                timeout={200} 
                unmountOnExit>
                <div className="recipe-details">
                    {props.recipe.ingredients.map(i => 
                        <p key={i.id} style={{textTransform: "capitalize"}}>
                            {strAssembly(i)}
                        </p>)}
                    <p>
                        {props.recipe.notes}
                    </p>
                    <div className="recipe-menu">
                        <IconButton onClick={deleteThis}>
                            <DeleteIcon className="recipe-icon" />
                        </IconButton>
                        <IconButton onClick={() => setExpanded(false)}>
                            <KeyboardArrowUpIcon className="recipe-icon" />
                        </IconButton>
                        <IconButton>
                            <EditIcon className="recipe-icon" />
                        </IconButton>
                    </div>
                </div>
            </Collapse>
        </div>
    );
}

export default RecipeEntry;