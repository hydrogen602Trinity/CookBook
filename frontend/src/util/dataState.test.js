import { renderHook, act } from '@testing-library/react-hooks';
import Fraction from 'fraction.js';
import { useRecipe } from './dataState';


test('basic useRecipe test', () => {
    const { result } = renderHook(() => useRecipe());

    act(() => {
        result.current.name = 'test';
    });

    expect(result.current.name).toBe('test');

    act(() => {
        result.current.notes = 'test123';
    });

    expect(result.current.notes).toBe('test123');
    expect(result.current.id).toBe(undefined);
});


test('basic useRecipe test 2', () => {
    const { result } = renderHook(() => useRecipe({name: 'A', notes: 'B', ingredients: []}));

    act(() => {
        result.current.name = 'test';
    });

    expect(result.current.name).toBe('test');

    act(() => {
        result.current.notes = 'test123';
    });

    expect(result.current.notes).toBe('test123');
});

test('basic useRecipe test 3', () => {
    const { result } = renderHook(() => useRecipe({id: 1, name: 'A', notes: 'B', ingredients: []}));

    expect(result.current.name).toBe('A');
    expect(result.current.notes).toBe('B');
    expect(result.current.ingredients.map(e => e)).toStrictEqual([]);
    expect(result.current.id).toBe(1);
});

test('basic useRecipe test 4', () => {
    const { result } = renderHook(() => useRecipe({name: 'A', notes: 'B', ingredients: []}));

    expect(result.current.name).toBe('A');
    expect(result.current.notes).toBe('B');

    act(() => {
        result.current.newIngredient();
    });

    expect(result.current.ingredients).toHaveLength(1);

    act(() => {
        result.current.ingredients[0].name = 'salt';
    });

    expect(result.current.ingredients[0].name).toBe('salt');
    expect(result.current.ingredients.map(e => e)).toHaveLength(1);
    expect(result.current.ingredients.map(e => e.name)).toStrictEqual(['salt']);

    act(() => {
        result.current.ingredients[0].amount = new Fraction(5);
    });

    expect(result.current.ingredients[0].amount).toStrictEqual(new Fraction(5));
    expect(result.current.ingredients[0].temp_amount).toBe('5');
});

// beforeEach(() => {
//     fetch.mockClear();
// });

test('fetch test 1', async () => {
    global.fetch = jest.fn(() => 
        Promise.resolve({
            json: () => Promise.resolve({
                id: 1,
                name: 'scrambled eggs',
                notes: 'beat eggs and fry in pan',
                ingredients: [
                    {
                        id: 1,
                        name: 'eggs',
                        num: 2,
                        denom: 1,
                        unit: '',
                    }
                ],
            }),
        })
    );

    const { result } = renderHook(() => useRecipe({id: 1}));

    await act(async () => {
        await result.current.refreshRecipe();
    });

    expect(result.current.name).toBe('scrambled eggs');
    expect(result.current.notes).toBe('beat eggs and fry in pan');
    expect(result.current.ingredients).toHaveLength(1);
    // expect(result.current.id).toBe(1);
});
