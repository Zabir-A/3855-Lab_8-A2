import { useState } from "react";
import "./App.css";
import Stats from "./components/Stats";

const App = () => {
  const [statuses, setStatuses] = useState({});

  const handleCheckHealthClick = async () => {
    try {
      const res = await fetch("http://34.130.96.245/health/check");
      const data = await res.json();
      console.log(data);
      setStatuses(data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="App">
      <h1>Dashboard</h1>
      <button onClick={handleCheckHealthClick}>Check Health</button>
      <div>
        {Object.keys(statuses).map((element) => {
          return (
            <div>
              {" "}
              {element}: {statuses[element]}{" "}
            </div>
          );
        })}
      </div>
      <Stats statuses={statuses} />
    </div>
  );
};

export default App;
