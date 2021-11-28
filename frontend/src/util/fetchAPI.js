// import { useEffect, useState, useCallback } from 'react';
// import { useEffect, useState } from "react";
import { useEffect } from "react";
import useFetch from "react-fetch-hook";
import { useNavigate } from "react-router";
import { useSnackbar } from "../components/Snackbar";

export function fullPath(path) {
    return 'http://' + process.env.REACT_APP_API + '/' + path;
}

export class AuthError extends Error {
    // constructor(message, options) {
    //     super(message, options);
    // }
}

export class APIError extends Error {
}


export function makeAuthErrorHandler(asyncFunc, onFailure) {
    return async function (...args) {
        let result = null;
        try {
            result = await asyncFunc(...args);
        }
        catch (err) {
            if (err instanceof AuthError) {
                return onFailure(err);
            }
            else {
                throw err;
            }
        }
        return result;
    }
}


export function useFetchAPI(path, dependsArray = null) {
    const dispatchMsg = useSnackbar();
    const nav = useNavigate();
    const args = {
        credentials: 'include',
    };
    if (dependsArray) {
        args.depends = dependsArray;
    }

    const { isLoading, data, error } = useFetch(
        fullPath(path), args);

    useEffect(() => {
        if (error) { 
            if (error.status === 401) {
                dispatchMsg({type: 'error', text: 'Authentication Required'});
                nav('/');
            }
            else {
                dispatchMsg({type: 'error', text: error.message})
            }
            // eslint-disable-next-line
        }}, [error]);

    return [isLoading, data, error];
}

// export function useFetchControlAPI(path) {
//     const [active, setActive] = useState(false);

//     const { isLoading, data, error } = useFetch(
//         fullPath(path),
//         active);

//     useEffect(() => {
//         if (!isLoading && active) {
//             setActive(false);
//         }
//     }, [isLoading]);

//     return [isLoading, data, error, setActive];
// }

export async function fetchControlAPI(path, method, data, json = true) {
    if (method !== 'GET' && method !== 'POST' && method !== 'PUT' && method !== 'DELETE') {
        throw new Error('Unknown HTTP Method');
    }
    const response = await fetch(fullPath(path), {
        method: method, // *GET, POST, PUT, DELETE, etc.
        // mode: 'cors', // no-cors, *cors, same-origin
        cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
        // credentials: 'same-origin', // include, *same-origin, omit
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(data)
    });
    if (!response.ok) {
        console.error(response.status, response.statusText);
        let t = await response.text();
        console.error(t);
    }

    if (response.status === 401) {
        throw new AuthError("Got a 401");
    }
    if (!response.ok) {
        throw new APIError(`${response.status}`);
    }
    // console.log(response);
    return json ? response.json() : response.text();
}

export async function fetchControlAPI2(path, method, data) {
    if (method !== 'GET' && method !== 'POST' && method !== 'PUT' && method !== 'DELETE') {
        throw new Error('Unknown HTTP Method');
    }
    return await fetch(fullPath(path), {
        method: method, // *GET, POST, PUT, DELETE, etc.
        // mode: 'cors', // no-cors, *cors, same-origin
        cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
        // credentials: 'same-origin', // include, *same-origin, omit
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(data)
    });
}

// export function useAPIState(path, onFailure = null) {
//     const fullPath = 'http://' + process.env.REACT_APP_API + '/' + path;
//     const [data, setData] = useState([]);

//     const onFailureFunc = useCallback(onFailure, []);

//     function update() {
//         fetch(fullPath)
//             .then(response => response.json())
//             .then(json => {
//                     setData(json);
//                 })
//             .catch((error) => {
//                 console.error('Error:', error);
//                 if (onFailureFunc) {
//                     onFailureFunc(error);
//                 }
//             });
//     }

//     useEffect(update, [fullPath, onFailureFunc]);

//     return [data, update];
// }

// export function getFetchAPIFunc(path, method = 'GET', onSuccess = null, onFailure = null) {
//     const fullPath = 'http://' + process.env.REACT_APP_API + '/' + path;

//     return (data) => {
//         fetch(fullPath, {
//             method: method,
//             body: JSON.stringify(data),
//             headers: {
//                 'Content-type': 'application/json'
//             }
//         })
//         .then(response => {
//             if (onSuccess) {
//                 onSuccess(response);
//             }
//             return response;
//         })
//         .catch((error) => {
//             if (onFailure) {
//                 onFailure(error);
//             }
//             console.error('Error:', error);
//         });
//     };
// }

export function fetchAPI(path, data, method = 'GET', onSuccess = null, onFailure = null) {
    const fullPath = 'http://' + process.env.REACT_APP_API + '/' + path;

    fetch(fullPath, {
        method: method,
        body: (data) ? JSON.stringify(data) : null,
        headers: {
            'Content-type': 'application/json'
        },
        credentials: 'include'
    })
    .then(response => {
        if (onSuccess) {
            onSuccess(response);
        }
        return response;
    })
    .catch((error) => {
        if (onFailure) {
            onFailure(error);
        }
        console.error('Error:', error);
    });
}
