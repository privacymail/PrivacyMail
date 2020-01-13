import React from "react";
import { BrowserRouter, Switch, Route } from "react-router-dom";
import Home from "./components/home/Home";
import Header from "./components/header/Header";
import Footer from "./components/footer/Footer";

function getRoutes() {
    const routes = [];

    routes.push(
        <Route key="/">
            <Home path="/" />
        </Route>
    );

    return routes;
}
class App extends React.Component {
    componentDidMount() {
        /**
         * This is here in order to address changing viewports on android phones when a keyboard is opened.
         * On the flipside on said phones the url bar now doesnt dissapers.
         */
        let viewheight = window.innerHeight;
        let viewwidth = window.innerWidth;
        let viewport = document.querySelector("meta[name=viewport]");
        viewport.setAttribute("content", "height=" + viewheight + "px, width=" + viewwidth + "px, initial-scale=1.0");
    }
    render() {
        return (
            <div>
                <Header />
                <div className="content">
                    <BrowserRouter>
                        <Switch>{getRoutes()}</Switch>
                    </BrowserRouter>
                </div>
                <Footer />
            </div>
        );
    }
}

export default App;
