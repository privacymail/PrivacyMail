import React from "react";
import logo from "../../assets/images/logo.png";
function Header() {
  return (
    <div className="header">
      <div>
        <img src={logo} alt=""></img>
        <h1>PrivacyMail</h1>
      </div>
    </div>
  );
}
export default Header;
