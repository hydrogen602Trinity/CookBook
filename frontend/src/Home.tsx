import "./Home.scss"
import "./Theme.scss"
import Button from '@mui/material/Button';
import useLogin from "./util/login";


export default function Home() {
    const login = useLogin();

    // login

    return (
    <div className="frame page-main">
        <div className="header">
            <h1>
                Home
            </h1>
            <div className="actions">
                <Button className="actions-buttons" onClick={login.doLogout}>
                    <i className="fas fa-sign-out-alt" style={{color: 'black'}}></i>
                </Button>
            </div>
        </div>
        
        <div className="main" id="content">

        </div>
    </div>
    )
}