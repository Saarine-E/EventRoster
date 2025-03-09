import { useState, useEffect } from "react";

const useCachedFetch = (url, cacheTime = 60000) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);

      // Retrieve cached data from localStorage
      const cachedData = localStorage.getItem(url);
      if (cachedData !== null) {
        const { data, timestamp } = JSON.parse(cachedData);

        // Check if cache is still valid
        if (Date.now() - timestamp < cacheTime) {
          setData(data);
          setLoading(false);
          return;
        }
      }

      // If no valid cache, fetch new data
      try {
        const response = await fetch(url);
        if (!response.ok) throw new Error("Failed to fetch");
        const result = await response.json();

        // Store new data in localStorage with a timestamp
        localStorage.setItem(url, JSON.stringify({ data: result, timestamp: Date.now() }));
        setData(result);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [url, cacheTime]);

  return { data, loading, error };
};

export default useCachedFetch;
