// import logo from './logo.svg';
// import './App.css';
import { useState, useEffect } from 'react';

function Note() {

    const [noteInput, setNoteInput] = useState('');
    const [notes, setNotes] = useState([]);

    function updateNotes() {
        fetch('http://' + process.env.REACT_APP_API + '/note')
            .then(response => response.json())
            .then(json => {
                    setNotes(json);
                })
            .catch((error) => {
                console.error('Error:', error);
            });
    }

    function submitNote() {
        fetch('http://' + process.env.REACT_APP_API + '/note', {
            method: "POST",
            body: JSON.stringify({note: noteInput}),
            headers: {
                'Content-type': 'application/json'
            }
        })
        .then(response => {
            updateNotes();
            return response;
        })
        .catch((error) => {
            console.error('Error:', error);
        });
        setNoteInput('');
    }

    useEffect(() => updateNotes(), []);

    return (
        <div className="frame">
            <div className="header">
                <h1>
                    Recipe Book
                </h1>
            </div>
            <div id="content">
                <ul>{ notes.map((note) => <li key={note.id}>{note.content}</li>) }</ul>
                <div>
                    <input name="note" value={noteInput} onChange={(ev) => setNoteInput(ev.target.value)}/>
                    <button name="submit" onClick={submitNote}>Submit</button>
                </div>
            </div>
        </div>
    );
}

export default Note;