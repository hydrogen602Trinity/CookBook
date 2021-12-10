import "./Home.scss"
import "./Theme.scss"
import Button from '@mui/material/Button';
import useLogin from "./util/login";
import { useSnackbar } from "./components/Snackbar";
import { useNavigate } from "react-router";
import { useCallback, useEffect, useState } from "react";
import createTrigger from "react-use-trigger";
import useTrigger from "react-use-trigger/useTrigger";
import { Select2Dates } from "./components/Form";
import { Dayjs } from 'dayjs';
import { useFetchControlAPI } from "./util/fetchAPI2";
import { useFetchAPI } from "./util/fetchAPI";


const checkLoginTrigger = createTrigger();

interface Ingredient {
    name: string,
    num: number,
    denom: number,
    unit: string
}

export default function Home() {
    const checkLoginTriggerValue = useTrigger(checkLoginTrigger);

    const [showNew, setShowNew] = useState(false);

    const login = useLogin();
    const dispatchMsg = useSnackbar();
    const nav = useNavigate();
    const sendToLogin = () => {
        dispatchMsg({type: 'error', text: 'Authentication Required'});
        nav('/');
    };

    useEffect(() => {
        login.checkLogin().then(user => {
            if (!user) {
                sendToLogin();
            }
        });
    }, [checkLoginTriggerValue, login]);

    const getShoppingList = useFetchControlAPI('/shoppinglist', 'GET', data => {
        setShopList(data);
    });

    const [shopList, setShopList] = useState([] as Ingredient[]);

    return (
    <div className="frame page-main home">
        <div className="header">
            <h1>
                Home
            </h1>
            <div className="actions">
                <Button className="actions-buttons" onClick={() => login.doLogout().then(_ => nav('/'))}>
                    <i className="fas fa-sign-out-alt" style={{color: 'black'}}></i>
                </Button>
            </div>
        </div>
        
        <div className="main" id="content">
            <Button onClick={() => setShowNew(true)} style={{color: 'black'}}>
                Create Shopping Plan
            </Button>
            <div className="shopping-out">
                {Object.entries(shopList).map(([k, v]) => {
                    return (
                        <div key={k}>
                            <span>{v.name}</span>
                            <span>{v.num}{v.denom > 1 ? '/' + v.denom : ''}</span>
                            <span>{v.unit}</span>
                        </div>
                    );
                })}
            </div>
        </div>
        <Select2Dates
            callback={(dates: Dayjs[]) => {
                const date1 = dates[0].format('YYYY-MM-DD');
                const date2 = dates[1].format('YYYY-MM-DD');

                // API call
                // console.log(date1, date2);
                getShoppingList(null, `/${date1}/${date2}`);
            }} 
            show={showNew}
            handleClose={() => setShowNew(false) }
        />
    </div>
    )
}