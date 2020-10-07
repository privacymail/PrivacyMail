import React from "react";
import { Switch, Route, Router } from "react-router-dom";
import Header from "./components/header/Header";
import Home from "./components/home/Home";
import Newsletter from "./components/newsletter/Newsletter";
import Footer from "./components/footer/Footer";
import ServiceNotFound from "./components/notfound/ServiceNotFound";

import { createBrowserHistory } from "history";
import Imprint from "./components/imprint/Imprint";
import NewSearch from "./components/newsletter/NewSearch";
import Privacy from "./components/privacy/Privacy";
import FAQ from "./components/faq/FAQ";
import Embed from "./components/embed/Embed";
import Identity from "./components/identity/Identity";
import Tooltip from "./utils/Tooltip";
import DefaultNotFound from "./components/notfound/DefaultNotFound";
import EmbedNotFound from "./components/notfound/EmbedNotFound";

/**
 * Generates all the routes required by PrivacyMail
 * @returns An array with all Routs used for this website
 */
const getRoutes = (): JSX.Element[] => {
    const routes: JSX.Element[] = [];

    routes.push(<Route key="/service/:id" path="/service/:id" children={<Newsletter />} />);
    routes.push(<Route key="/embed/:id" path="/embed/:id" children={<Embed />} />);

    routes.push(
        <Route key="/" path="/" exact>
            <Home />
        </Route>
    );
    routes.push(
        <Route key="/imprint" path="/imprint">
            <Imprint />
        </Route>
    );
    routes.push(
        <Route key="/privacy" path="/privacy">
            <Privacy />
        </Route>
    );
    routes.push(
        <Route key="/faq" path="/faq">
            <FAQ />
        </Route>
    );
    routes.push(
        <Route key="/identity" path="/identity/:id">
            <Identity />
        </Route>
    );
    routes.push(
        <Route key="/serviceNotFound" path="/serviceNotFound/:id">
            <ServiceNotFound />
        </Route>
    );
    routes.push(
        <Route key="/embedNotFound" path="/embedNotFound/:id">
            <EmbedNotFound />
        </Route>
    );
    routes.push(
        <Route key="/404">
            <DefaultNotFound />
        </Route>
    );
    return routes;
};

const App = () => {
    const history = createBrowserHistory();
    //This resets the page to scroll back to the top on URL changes
    history.listen(() => {
        window.scrollTo(0, 0);
    });

    return (
        <div className="app">
            <Router history={history}>
                <Header />

                <Switch>
                    <Route key="/" path="/" exact>
                        <div className="page">
                            <Home />

                            <Footer />
                        </div>
                    </Route>
                    <Route key="/newSearch" path="*/:id">
                        <NewSearch />
                        <div className="page">
                            <div className="content">
                                <Switch>{getRoutes()}</Switch>
                            </div>

                            <Footer />
                        </div>
                    </Route>
                </Switch>
            </Router>
            <Tooltip />
        </div>
    );
};

export default App;
