import './Recipes.css'

export default function Recipes() {
    return (
        <div className="frame">
            <div className="header">
                <h1>
                    Recipe Book
                </h1>
                <button>
                    <i className="fas fa-plus"></i>
                </button>
            </div>
            {/* <div className="bar" hidden={true}>
                <button>New</button>
                <button>Edit</button>
                <button>Delete</button>
            </div> */}
            <div className="main" id="content"></div>
            {/* <div className="sidebar" hidden={true}>
                <button onClick={() => console.log('getAllRecipes')}>
                    Recipes
                </button>
            </div> */}
        </div>
    );
}