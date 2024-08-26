import React from "react";
import "mapbox-gl/dist/mapbox-gl.css";
import Map from "react-map-gl";

const MapboxComponent = () => {
  return (
    <div
      id="mapboxContainer"
      style={{ width: "100vw", height: "calc(100% - 160px)" }}
    >
      <Map
        const
        mapboxAccessToken={process.env.REACT_APP_MAPBOX_ACCESS_TOKEN}
        initialViewState={{
          longitude: -122.4,
          latitude: 37.8,
          zoom: 14,
        }}
        style={{ width: "100%", height: "100%" }}
        mapStyle="mapbox://styles/mapbox/streets-v9"
      />
    </div>
  );
};

export default MapboxComponent;
