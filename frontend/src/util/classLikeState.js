import { useState } from "react";


function useBetterState(defaultValues) {
    const [state, setState] = useState(defaultValues);

    function newSetState(nextState) {
        setState(prevState => ({
            ...prevState,
            ...nextState
        }));
    }
    
    return [state, newSetState];
}

export default useBetterState;