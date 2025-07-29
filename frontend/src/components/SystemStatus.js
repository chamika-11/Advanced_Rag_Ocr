import React, { useEffect, useState } from "react";
import axios from "axios";

function SystemStatus() {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    axios.get("http://localhost:8000/system-status/")
      .then((res) => setStatus(res.data))
      .catch(() => setStatus(null));
  }, []);

  return (
    <div className="bg-white shadow-md rounded p-4 mb-6">
      <h2 className="text-xl font-semibold mb-2">System Status</h2>
      {status ? (
        <ul className="list-disc pl-5 text-sm">
          <li>Initialized: {status.system_initialized ? "Yes" : "No"}</li>
          <li>Total Docs: {status.total_documents}</li>
          <li>Memory Active: {status.memory_active ? "Yes" : "No"}</li>
          <li>Available Tools: {status.available_tools.join(", ")}</li>
        </ul>
      ) : (
        <p className="text-red-600">Failed to load system status.</p>
      )}
    </div>
  );
}

export default SystemStatus;
