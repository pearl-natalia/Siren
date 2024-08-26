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
        mapboxAccessToken="pk.eyJ1IjoicGVhcmxuYXRhbGlhIiwiYSI6ImNtMGEzeG9mbjE4N3EybnBwajBkeW1zcDMifQ.5l4d-w-_k3w1vkYEy4RJOg"
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
