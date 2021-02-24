'use strict';

const domain = ""; //"http://localhost:5000/";

const recipesBox = {
    rootID: 'content',
    recipes: [],

    buildAll: function () {
        const root = document.getElementById(this.rootID);

        this.recipes.forEach(r => {
            const oldRef = r.ref;
            if (oldRef) {
                root.replaceChild(r.build(), oldRef);
            }
            else {
                root.append(r.build());
            }
        });
    },

    deleteRow: function (elem) {
        const root = document.getElementById(this.rootID);
        root.removeChild(elem);
        this.recipes = this.recipes.filter(r => r.ref != elem);
    },

    updateRecipes: function () {
        util.doREST('GET', 'allrecipes', (text) => {
            const data = JSON.parse(text).sort((a, b) => (a[1] == b[1]) ? 0 : (a[1] > b[1]) ? 1 : -1);

            this.recipes = [];

            data.forEach(e => {
                let name = e[1];
                let id = e[0];

                this.recipes.push(new Recipe(name, id));
            });

            recipesBox.buildAll();
        });
    } 
};

// for compatibility
const getAllRecipes = recipesBox.updateRecipes.bind(recipesBox);

const util = {
    createIcon: function (clsNames) {
        const icon = document.createElement('i');
        for (const cls of clsNames.split(' ')) {
            icon.classList.add(cls);
        }
        return icon;
    },

    doREST: function (method, path, callback, body=undefined) {
        const xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                callback(xhttp.responseText);
            }
            else if (this.readyState == 4) {
                throw Error('Got error code ' + this.status + ' on request ' + method + ' ' + path);
            }
        };
        xhttp.open(method, domain + path, true);
        xhttp.send(body);
    }
};

class Recipe {
    constructor(name, id) {
        this.name = name;
        this.id = id;

        this.recipeData = undefined;

        this.expanded = false;
        this.ref = undefined;

        this.needsUpdate = true;
        this.editMode = false;

        this.tempRecipeData = undefined;
    }

    toJson() {
        // only call after loading recipeData!
        if (!this.recipeData) {
            throw Error('Recipe must be fully loaded');
        }

        return JSON.stringify({
           'recipeName': this.name,
           'ingredients': this.recipeData.ingredients,
           'instructions': this.recipeData.instructions,
           'notes': this.recipeData.notes,
           'id': this.id
        });
    }

    fetchData(onComplete) {
        util.doREST('GET', 'recipe/' + this.id, (text) => {
            const data = JSON.parse(text);

            //const name = data["recipeName"];
            const id = data["id"];
            if (id != this.id) {
                throw Error('ID received does not match requested');
            }

            const ingredients = data['ingredients'];
            const instructions = data['instructions'];
            const notes = data['notes'];

            this.recipeData = new RecipeData(ingredients, instructions, notes);
            onComplete();
        });
    }

    expand() {
        this.fetchData(() => {
            this.expanded = true;
            this.needsUpdate = true;
            recipesBox.buildAll();
        });
        //getRecipe(id)
    }

    collapse() {
        this.expanded = false;
        this.needsUpdate = true;
        // content.replaceChild(createRecipeButton(this.name, this.id), recipeBox);
        recipesBox.buildAll();
    }

    build() {
        if (!this.needsUpdate) {
            return this.ref;
        }
        this.needsUpdate = false;

        console.log("building " + this.name);
        if (this.expanded) {
            if (this.editMode) {
                if (!this.tempRecipeData) {
                    this.tempRecipeData = this.recipeData.copy();
                }
            }

            const box = document.createElement("div");
            box.classList.add("recipe");

            let recipeTitle = document.createElement("div");
            recipeTitle.innerText = this.name;
            recipeTitle.classList.add("recipeName");
            box.append(recipeTitle);

            const ingredients = ((this.editMode) ? this.tempRecipeData : this.recipeData).ingredients.map(e =>
                e['amount'] + ' ' + e['unit'] + ' ' + e['name']
            );
            const instructions = ((this.editMode) ? this.tempRecipeData : this.recipeData).instructions;
            const notes = ((this.editMode) ? this.tempRecipeData : this.recipeData).notes;

            let funcArr = (this.editMode) ? ingredients.map((e, i) => this.tempRecipeData.generateOnIngredientChange(i)) : undefined;

            box.append(this._createRecipeDisplay('Ingredients', ingredients, funcArr, 'ul'));

            // if (this.editMode) {
            //     box.append(helper('fas fa-plus'));
            // }
            funcArr = (this.editMode) ? instructions.map((e, i) => this.tempRecipeData.generateOnInstructionsChange(i)) : undefined;
            

            box.append(this._createRecipeDisplay('Instructions', instructions, funcArr));

            const func = (this.editMode) ? this.tempRecipeData.onNotesChange.bind(this.tempRecipeData) : undefined;

            box.append(this._createRecipeDisplay('Notes', notes, func));

            if (this.editMode) {
                box.append(this._createEditOptions());
            }
            else {
                box.append(this._createOptions());
            }

            this.ref = box;
        }
        else {
            const elem = document.createElement("div");
            elem.innerText = this.name;
            elem.onclick = this.expand.bind(this);
            elem.classList.add('unselectable');

            this.ref = elem;
        }

        return this.ref;
    }

    _createRecipeDisplay(titleName, stringOrArr, funcOrArr=undefined, listStyle='ol') {
        const box = document.createElement('div');
        const title = document.createElement('h3');
        title.innerText = titleName;
        title.style.margin = "0";
        box.append(title);

        const createInput = function (text, onchange) {
            const input = document.createElement('input');
            input.value = text;
            input.onchange = onchange;
            return input;
        }

        const createButton = (iconCls) => {
            const button = document.createElement('button');
            button.classList.add('addLineEdit');
            button.append(util.createIcon(iconCls));
            return button;
        };

        if (Array.isArray(stringOrArr)) {
            if (this.editMode) {
                if (!Array.isArray(funcOrArr) || funcOrArr.length != stringOrArr.length) {
                    throw Error("funcOrArr should be the same length as stringOrArr");
                }
                title.appendChild(createButton('fas fa-plus'));
            }

            const list = document.createElement(listStyle);
            stringOrArr.forEach((e, index) => {
                const func = (funcOrArr) ? funcOrArr[index] : undefined;

                const elem = document.createElement('li');
                if (this.editMode) {
                    
                    elem.appendChild(createInput(e, func));
                    elem.appendChild(createButton('fas fa-minus-circle'));
                }
                else {
                    elem.innerText = e;
                }
                
                list.append(elem);
            });
            box.append(list);
        }
        else {
            const oneStr = document.createElement('p');
            if (this.editMode) {
                if (Array.isArray(funcOrArr)) {
                    throw Error("stringOrArr is not array, but funcOrArr is");
                }
                oneStr.appendChild(createInput(stringOrArr, funcOrArr));
            }
            else {
                oneStr.innerText = stringOrArr;
            }
            box.append(oneStr);
        }

        return box;
    }

    _createOptions() {
        const box = document.createElement('div');
        box.style.display = 'flex';
        box.style.flexDirection = 'row';
        box.style.justifyContent = 'space-between';

        const helper = (iconCls) => {
            const button = document.createElement('button');
            button.classList.add('editOrDel');
            button.append(util.createIcon(iconCls));
            return button;
        };
    
        const deleteButton = helper("fas fa-trash-alt");
        deleteButton.onclick = this.delete.bind(this);
    
        const collapseButton = helper("fas fa-chevron-up");
        collapseButton.onclick = this.collapse.bind(this);
    
        const editButton = helper("fas fa-edit");
        editButton.onclick = this.editEntry.bind(this);
    
        box.append(deleteButton);
        box.append(collapseButton);
        box.append(editButton);
    
        return box;
    }

    _createEditOptions() {
        const box = document.createElement('div');
        box.style.display = 'flex';
        box.style.flexDirection = 'row';
        box.style.justifyContent = 'space-between';

        const helper = (iconCls) => {
            const button = document.createElement('button');
            button.classList.add('editOrDel');
            button.append(util.createIcon(iconCls));
            return button;
        };
    
        const deleteButton = helper("fas fa-trash-alt");
        deleteButton.onclick = this.delete.bind(this);
    
        const saveButton = helper("fas fa-save");
        saveButton.onclick = this.saveEntry.bind(this);
    
        box.append(deleteButton);
        box.append(saveButton);
    
        return box;
    }

    delete() {
        if (!confirm('Are you sure you want to delete the ' + this.name + ' recipe')) {
            return; // delete cancelled
        }

        util.doREST('DELETE', 'recipe/' + this.id, (text) => {
            recipesBox.deleteRow(this.ref);
        });
    }

    editEntry() {
        this.editMode = true;
        this.needsUpdate = true;
        recipesBox.buildAll();
    }

    saveEntry() {
        this.editMode = false;

        if (this.tempRecipeData) {
            this.recipeData = this.tempRecipeData;
        }
        this.tempRecipeData = undefined;

        // send the data!
        util.doREST('PUT', 'recipe/' + this.id, () => {}, this.toJson());
        console.log(this);

        this.needsUpdate = true;
        recipesBox.buildAll();
    }
}

class RecipeData {
    constructor(ingredients, instructions, notes) {
        this.ingredients = ingredients; // list of {}
        // with keys name, amount, & unit
        this.notes = notes; // string
        this.instructions = instructions; // list of strings
    }

    copy() {
        const deepCopy = (obj) => JSON.parse(JSON.stringify(obj));

        return new RecipeData(deepCopy(this.ingredients), deepCopy(this.instructions), deepCopy(this.notes));
    }

    onNotesChange(ev) {
        this.notes = ev.target.value;
    }

    generateOnInstructionsChange(index) {
        return (ev) => {
            this.instructions[index] = ev.target.value;
        };
    }

    generateOnIngredientChange(index) {
        return (ev) => {
            alert("Not yet supported");
        };
    }
}