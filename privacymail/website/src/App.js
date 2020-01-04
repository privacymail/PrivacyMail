import React from "react";
import { BrowserRouter, Switch, Route } from "react-router-dom";
import Home from "./components/home/Home";
import Header from "./components/header/Header";

function getRoutes() {
    const routes = [];

    routes.push(
        <Route>
            <Home path="/" />
        </Route>
    );

    return routes;
}
function App() {
    return (
        <div>
            <Header />
            <div className="content">
                <BrowserRouter>
                    <Switch>{getRoutes()}</Switch>
                </BrowserRouter>
            </div>
        </div>
    );
}

export default App;
