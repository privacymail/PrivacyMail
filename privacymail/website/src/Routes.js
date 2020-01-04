import React from "react";
import { Trans } from "react-i18next";
import { BrowserRouter, Switch, Route } from "react-router-dom";
import Home from "./components/home/Home";

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
        <BrowserRouter>
            <Switch>{getRoutes()}</Switch>
        </BrowserRouter>
    );
}

export default App;
