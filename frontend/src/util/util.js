
// https://stackoverflow.com/questions/7616461/generate-a-hash-from-string-in-javascript
export function simpleHash(s) {
    let hash = 0;
    if (s.length === 0) return hash;
    for (let i = 0; i < s.length; i++) {
        const chr = s.charCodeAt(i);
        hash = ((hash << 5) - hash) + chr;
        hash |= 0;
    }
    return hash;
}