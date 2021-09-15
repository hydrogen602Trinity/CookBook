import { useState } from "react";


function useBetterState(defaultValues) {
    const [state, setState] = useState(defaultValues);

    function newSetState(nextState) {
        if (typeof nextState === 'function') {
            setState(prevState => ({
                ...prevState,
                ...nextState(prevState)
            }));
        }
        else {
            setState(prevState => ({
                ...prevState,
                ...nextState
            }));
        }
    }
    
    return [state, newSetState];
}

export default useBetterState;