import { useEffect, useState } from 'react';

export function useAPIState(path) {
    const fullPath = 'http://' + process.env.REACT_APP_API + '/' + path;
    const [data, setData] = useState([]);

    function update() {
        fetch(fullPath)
            .then(response => response.json())
            .then(json => {
                    setData(json);
                })
            .catch((error) => {
                console.error('Error:', error);
            });
    }

    useEffect(update, [fullPath]);

    return [data, update];
}

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
        body: JSON.stringify(data),
        headers: {
            'Content-type': 'application/json'
        }
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
