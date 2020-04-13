import React from "react";
import { Switch, Route, Router } from "react-router-dom";
import Header from "./components/header/Header";
import Home from "./components/home/Home";
import Newsletter from "./components/newsletter/Newsletter";
import Footer from "./components/footer/Footer";
import NotFound from "./components/notfound/NotFound";

import { createBrowserHistory } from "history";
import Imprint from "./components/imprint/Imprint";

const getRoutes = () => {
    const routes = [];

    routes.push(<Route key="/service/:id" path="/service/:id" children={<Newsletter />} />);
    routes.push(
        <Route key="/404" path="/404/:id">
            <NotFound />
        </Route>
    );
    routes.push(
        <Route key="/imprint" path="/imprint">
            <Imprint />
        </Route>
    );
    routes.push(
        <Route key="/" path="/">
            <Home />
        </Route>
    );

    return routes;
};

const App = () => {
    const history = createBrowserHistory();
    history.listen(() => {
        window.scrollTo(0, 0);
    });

    return (
        <div className="app">
            <Router history={history}>
                <Header />
                <div className="content">
                    <div className="content-inside">
                        <Switch>{getRoutes()}</Switch>
                    </div>
                </div>
                <Footer />
            </Router>
        </div>
    );
};

export default App;
