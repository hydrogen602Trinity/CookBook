const domain = ""; //"http://localhost:5000/";

let recipes = [];

function doREST(method, path, callback) {
    const xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            callback(xhttp.responseText);
        }
    };
    xhttp.open(method, domain + path, true);
    xhttp.send();
}

function getAllRecipes() {
    doREST('GET', 'allrecipes', (text) => {
        data = JSON.parse(text);

        const content = document.getElementById("content");
        content.innerHTML = "";

        data = data.sort((a, b) => (a == b) ? 0 : (a < b) ? 1 : -1);

        data.forEach(e => {
            let name = e[1];
            let id = e[0];

            content.append(createRecipeButton(name, id));
        });

        recipes = data;
    });
}

function getRecipe(id) {
    doREST('GET', 'recipe/' + id, (text) => {
        data = JSON.parse(text);

        const content = document.getElementById("content");
        const name = data["recipeName"];
        const id = data["_Recipe__uuid"];

        const box = document.createElement("div");
        box.classList.add("recipe");
        // box.onclick = () => {
        //     content.replaceChild(createRecipeButton(name, id), box);
        // };

        let recipeTitle = document.createElement("div");
        recipeTitle.innerText = name;
        recipeTitle.classList.add("recipeName");
        box.append(recipeTitle);

        const ingredients = data['ingredients'].map(e =>
            e['name'] + ': ' + e['amount'] + ' ' + e['unit']
        );
        const instructions = data['instructions'];
        const notes = data['notes'];

        box.append(createRecipeDisplay('Ingredients', ingredients));

        box.append(createRecipeDisplay('Instructions', instructions));

        box.append(createRecipeDisplay('Notes', notes));

        for (e of content.children) {
            if (e.innerText.toUpperCase() == name.toUpperCase()) {
                content.replaceChild(box, e);
                break;
            }
        }

        box.append(createOptions(name, id, content, box));
    })
}

function createRecipeButton(name, id) {
    let elem = document.createElement("div");
    elem.innerText = name;
    elem.onclick = () => getRecipe(id);
    elem.classList.add('unselectable');
    return elem;
}

function createRecipeDisplay(titleName, stringOrArr) {
    const box = document.createElement('div');
    const title = document.createElement('h3');
    title.innerText = titleName;
    title.style.margin = "0px";
    box.append(title);

    if (Array.isArray(stringOrArr)) {
        const list = document.createElement('ol');
        for (e of stringOrArr) {
            let elem = document.createElement('li');
            elem.innerText = e;
            list.append(elem);
        }
        box.append(list);
    }
    else {
        const oneStr = document.createElement('p');
        oneStr.innerText = stringOrArr;
        box.append(oneStr);
    }

    return box;
}

function createIcon(clsNames) {
    const icon = document.createElement('i');
    for (cls of clsNames.split(' ')) {
        icon.classList.add(cls);
    }
    return icon;
}

function createOptions(name, id, content, recipeBox) {
    const box = document.createElement('div');
    box.style.display = 'flex';
    box.style.flexDirection = 'row';
    box.style.justifyContent = 'space-between';

    const deleteButton = document.createElement('button');
    deleteButton.classList.add('editOrDel');
    deleteButton.append(createIcon("fas fa-trash-alt"));

    const collapseButton = document.createElement('button');
    collapseButton.classList.add('editOrDel');
    collapseButton.append(createIcon("fas fa-chevron-up"));
    collapseButton.onclick = () => {
        content.replaceChild(createRecipeButton(name, id), recipeBox);
    };

    const editButton = document.createElement('button');
    editButton.classList.add('editOrDel');
    editButton.append(createIcon("fas fa-edit"));

    box.append(deleteButton);
    box.append(collapseButton);
    box.append(editButton);

    return box;
}