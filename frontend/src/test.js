import { fetchControlAPI } from './util/fetchAPI';

export async function testLogin() {
    let result = null;
    try {
        result = await fetchControlAPI('login', 'POST', {email: 'jrotter@trinity.edu', password: 'postgres'});
    }
    catch (err) {
        console.error('login', err);
        // setError(err + '');
        throw err;
    }
    // console.log(await fetchControlAPI('login', 'GET'));
    // console.log('response', result);
    return result;
}

export async function testLogout() {
    let result = null;
    try {
        result = await fetchControlAPI('login', 'DELETE');
    }
    catch (err) {
        console.error('login', err);
        // setError(err + '');
        throw err;
    }
    // console.log(await fetchControlAPI('login', 'GET'));
    // console.log('response', result);
    return result;
}