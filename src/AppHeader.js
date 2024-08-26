// src/AppHeader.js
import React from "react";

const AppHeader = React.forwardRef((props, ref) => (
  <header className="App-header" ref={ref}>
    <h1>Siren Dashcam</h1>
    {/* Add more header content if needed */}
  </header>
));

export default AppHeader;
