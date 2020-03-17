import React from "react";
import ReactDOM from "react-dom";
import { Trans, withTranslation } from "react-i18next";
import { Parallax, ParallaxBase, ParallaxBackground } from "../../utils/Parallax";
import letterImg from "../../assets/images/letter.jpg";
import { IconList, IconListItem } from "../../utils/IconList";

class Home extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            stats: {}
        };
    }

    render() {
        return (
            <div className="home">
                <div className="grid" ref={this.gridRef}>
                    <h1 className="grid-item light">
                        <Trans>home_headline</Trans>
                    </h1>
                    <h3 className="grid-item light">
                        <Trans>home_subheadline</Trans>
                    </h3>
                    <div className="grid-divider" />
                    <div className="grid-item input">
                        <input type="text" placeholder={this.props.t("home_inputPlaceholder")} />
                        <button>
                            <Trans>home_analyise</Trans>
                        </button>
                    </div>
                    <div className="grid-divider" />
                    <div className="grid-item-4 statistic">
                        <p className="medium big">69.933</p>
                        <p className="regular normal">
                            <Trans>home_emailsAnalysied</Trans>
                        </p>
                    </div>
                    <div className="grid-item-4 statistic">
                        <p className="medium big">2.928</p>
                        <p className="regular normal">
                            <Trans>home_found3rdPraties</Trans>
                        </p>
                    </div>
                    <div className="grid-item-4 statistic">
                        <p className="medium big">1.363</p>
                        <p className="regular normal">
                            <Trans>home_registeredNewsletters</Trans>
                        </p>
                    </div>

                    <div className="grid-divider" />
                    <h2 className="grid-item regular">
                        <Trans>home_shiningALight</Trans>
                    </h2>
                    <div className="grid-item">
                        <p className="normal light">
                            <Trans>home_shiningALightDetail</Trans>
                        </p>
                    </div>

                    <div className="grid-divider" />
                    <h2 className="grid-item regular">
                        <Trans>home_howItWorks</Trans>
                    </h2>
                    <IconList className="image-list grid-item">
                        <IconListItem icon={"email"}>
                            <Trans>home_howItWorks1</Trans>
                        </IconListItem>
                        <IconListItem icon={"done_all"}>
                            <Trans>home_howItWorks2</Trans>
                        </IconListItem>
                        <IconListItem icon={"insert_link"}>
                            <Trans>home_howItWorks3</Trans>
                        </IconListItem>
                        <IconListItem icon={"attach_money"}>
                            <Trans>home_howItWorks4</Trans>
                        </IconListItem>
                    </IconList>

                    <div className="grid-divider" />
                    <h2 className="grid-item regular">
                        <Trans>home_howWeDetectIt</Trans>
                    </h2>
                    <IconList className="image-list grid-item">
                        <IconListItem icon={"email"}>
                            <Trans>home_howWeDetectIt1</Trans>
                        </IconListItem>
                        <IconListItem icon={"search"}>
                            <Trans>home_howWeDetectIt2</Trans>
                        </IconListItem>
                        <IconListItem icon={"public"}>
                            <Trans>home_howWeDetectIt3</Trans>
                        </IconListItem>
                        <IconListItem icon={"mood"}>
                            <Trans>home_howWeDetectIt4</Trans>
                        </IconListItem>
                    </IconList>

                    <div className="grid-divider" />
                    <h2 className="grid-item regular">
                        <Trans>home_whyUsePM</Trans>
                    </h2>
                    <IconList className="image-list grid-item">
                        <IconListItem icon={"email"}>
                            <p className="medium big">
                                <Trans>home_whyUsePM1</Trans>
                            </p>
                            <p className="normal light">
                                <Trans>home_whyUsePM1detail</Trans>
                            </p>
                        </IconListItem>
                        <IconListItem icon={"record_voice_over"}>
                            <p className="medium big">
                                <Trans>home_whyUsePM2</Trans>
                            </p>
                            <p className="normal light">
                                <Trans>home_whyUsePM2detail</Trans>
                            </p>
                        </IconListItem>
                        <IconListItem icon={"school"}>
                            <p className="medium big">
                                <Trans>home_whyUsePM3</Trans>
                            </p>
                            <p className="normal light">
                                <Trans>home_whyUsePM3detail</Trans>
                            </p>
                        </IconListItem>
                    </IconList>
                </div>
            </div>
        );
    }
}

export default withTranslation()(Home);
