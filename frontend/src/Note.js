// import logo from './logo.svg';
// import './App.css';
import { useState } from 'react';
import { fetchAPI, useAPIState } from './util/fetchAPI';

function Note() {

    const [noteInput, setNoteInput] = useState('');
    const [notes, updateNotes] = useAPIState('note');

    function submitNote() {
        fetchAPI('note', {note: noteInput}, 'POST', res => {
            updateNotes();
            setNoteInput('');
        });
    }

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