import { useState } from "react";
import Collapse from '@material-ui/core/Collapse';
import './RecipeEntry.css'


function RecipeEntry(props) {
    const [isExpanded, setExpanded] = useState(false);

    function strAssembly(i) {
        return `${i.name}: ${i.num}${i.denom > 1 ? '/'+i.denom : ''}${i.unit ? ' '+i.unit : ''}`
    }

    return (
        <div onClick={() => setExpanded(!isExpanded)} className="recipe-entry">
            <div>
                {props.recipe.name}
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
                </div>
            </Collapse>
        </div>
    );
}

export default RecipeEntry;