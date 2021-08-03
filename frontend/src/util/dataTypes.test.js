import Fraction from "fraction.js";
import { Ingredient, serialize_ingredient } from "./dataTypes";

test('ingredient', () => {

    const f = new Ingredient();

    expect(f.amount.n).toBe(1);
    expect(f.amount.d).toBe(1);
    expect(f.amount.s).toBe(1);
    expect(f.name).toBe('');
    expect(f.unit).toBe('');
    expect(f.temp_amount).toBe('1');
    expect(f.id).toBe(undefined);
});

test('ingredient', () => {

    const f = new Ingredient({
        name: 'salt',
        unit: 'g',
        num: 2,
        denom: 1,
        id: 1
    });

    expect(f.amount.n).toBe(2);
    expect(f.amount.d).toBe(1);
    expect(f.amount.s).toBe(1);
    expect(f.name).toBe('salt');
    expect(f.unit).toBe('g');
    expect(f.temp_amount).toBe('2');
    expect(f.id).toBe(1);
    expect(f.num).toBe(undefined);
    expect(f.denom).toBe(undefined);
});

test('ingredient', () => {

    const f = new Ingredient({
        name: 'salt',
        unit: 'g',
        num: 2,
        denom: 1,
        id: 1
    });

    f.amount = new Fraction(5,2);
    f.unit = 'kg';

    const data = serialize_ingredient(f);

    expect(data.num).toBe(5);
    expect(data.denom).toBe(2);
    expect(data.name).toBe('salt');
    expect(data.unit).toBe('kg');
    expect(data.amount).toBe(undefined);
    expect(data.temp_amount).toBe(undefined);
    expect(data.id).toBe(1);
});