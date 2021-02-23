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

    doREST: function (method, path, callback) {
        const xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                callback(xhttp.responseText);
            }
        };
        xhttp.open(method, domain + path, true);
        xhttp.send();
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
    }

    fetchData(onComplete) {
        util.doREST('GET', 'recipe/' + this.id, (text) => {
            const data = JSON.parse(text);
            //const name = data["recipeName"];
            const id = data["_Recipe__uuid"];
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
            const box = document.createElement("div");
            box.classList.add("recipe");

            let recipeTitle = document.createElement("div");
            recipeTitle.innerText = this.name;
            recipeTitle.classList.add("recipeName");
            box.append(recipeTitle);

            const ingredients = this.recipeData.ingredients.map(e =>
                e['amount'] + ' ' + e['unit'] + ' ' + e['name']
            );
            const instructions = this.recipeData.instructions;
            const notes = this.recipeData.notes;

            const helper = (iconCls) => {
                const button = document.createElement('button');
                button.classList.add('addLineEdit');
                button.append(util.createIcon(iconCls));
                return button;
            };

            box.append(this._createRecipeDisplay('Ingredients', ingredients, 'ul'));

            if (this.editMode) {
                box.append(helper('fas fa-plus'));
            }
            

            box.append(this._createRecipeDisplay('Instructions', instructions));
            box.append(this._createRecipeDisplay('Notes', notes));

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

    _createRecipeDisplay(titleName, stringOrArr, listStyle='ol') {
        const box = document.createElement('div');
        const title = document.createElement('h3');
        title.innerText = titleName;
        title.style.margin = "0";
        box.append(title);

        const createInput = function (text) {
            const input = document.createElement('input');
            input.value = text;
            return input;
        }

        if (Array.isArray(stringOrArr)) {
            const list = document.createElement(listStyle);
            for (const e of stringOrArr) {
                const elem = document.createElement('li');
                if (this.editMode) {
                    elem.appendChild(createInput(e));
                }
                else {
                    elem.innerText = e;
                }
                
                list.append(elem);
            }
            box.append(list);
        }
        else {
            const oneStr = document.createElement('p');
            if (this.editMode) {
                oneStr.appendChild(createInput(stringOrArr));
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
}