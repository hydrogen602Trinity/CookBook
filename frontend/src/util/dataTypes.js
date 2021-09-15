import Fraction from "fraction.js";
import { convertFraToStr, isInteger } from "./util";


export function Ingredient(ingredient = null) {
    this.name = '';
    this.amount = new Fraction(1);
    this.temp_amount = '1';
    this.unit = '';

    if (ingredient) {
        if (isInteger(ingredient.num) && isInteger(ingredient.denom)) {
            this.amount = new Fraction(ingredient.num, ingredient.denom);
            this.temp_amount = convertFraToStr(this.amount);
        }
        if (ingredient.name) {
            this.name = ingredient.name;
        }
        if (ingredient.unit) {
            this.unit = ingredient.unit;
        }
        if (ingredient.id) {
            this.id = ingredient.id;
        }
    }
}

export function serialize_ingredient(i) {
    const newIngredient = {...i};
    newIngredient.num = i.amount.n * i.amount.s;
    newIngredient.denom = i.amount.d;
    delete newIngredient.amount;
    delete newIngredient.temp_amount;
    return newIngredient;
}
