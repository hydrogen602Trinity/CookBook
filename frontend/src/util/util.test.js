import { isInteger } from "./util";

test('isInteger', () => {

    expect(isInteger(1)).toBe(true);
    expect(isInteger(-1)).toBe(true);
    expect(isInteger(1234567890)).toBe(true);
    expect(isInteger(0)).toBe(true);
    expect(isInteger(3.0)).toBe(true);

    expect(isInteger(1.1)).toBe(false);
    expect(isInteger(-1.01)).toBe(false);
    expect(isInteger('123a456')).toBe(false);
    expect(isInteger(null)).toBe(false);
    expect(isInteger(undefined)).toBe(false);
    expect(isInteger('')).toBe(false);
    expect(isInteger('hello')).toBe(false);
});