import Fraction from "fraction.js";

// https://stackoverflow.com/questions/7616461/generate-a-hash-from-string-in-javascript
export function simpleHash(s: string): number {
    let hash = 0;
    if (s.length === 0) return hash;
    for (let i = 0; i < s.length; i++) {
        const chr = s.charCodeAt(i);
        hash = ((hash << 5) - hash) + chr;
        hash |= 0;
    }
    return hash;
}

export function convertFraToStr(f: string | Fraction): string {
    if (typeof f === 'string') {
        return f;
    }
    return `${f.s * f.n}${f.d > 1 ? '/'+f.d : ''}`
}

export function isInteger(n: number | string): boolean {
    const numBackToStr = parseInt(n + '') + '';
    return numBackToStr !== 'NaN' && numBackToStr === n + '';
}

export function cleanQuotes(str: string): string {
    let s = str.trim();
    if (s[0] === '"' || s[0] === "'") {
        s = s.substring(1);
    }
    if (s[s.length-1] === '"' || s[s.length-1] === "'") {
        s = s.substring(0,s.length-1);
    }
    return s;
}
