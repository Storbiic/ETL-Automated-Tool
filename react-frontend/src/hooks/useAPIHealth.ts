import { useState, useEffect } from 'react';

export const useAPIHealth = () => {
  const [isHealthy, setIsHealthy] = useState(false);
  const [isChecking, setIsChecking] = useState(true);
  const [retryCount, setRetryCount] = useState(0);

  const checkHealth = async () => {
    try {
      setIsChecking(true);

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      const response = await fetch('http://localhost:8000/', {
        method: 'GET',
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        setIsHealthy(true);
        setRetryCount(0); // Reset retry count on success
      } else {
        setIsHealthy(false);
      }
    } catch (error) {
      setIsHealthy(false);
      console.log('API health check failed:', error);
    } finally {
      setIsChecking(false);
    }
  };

  useEffect(() => {
    // Initial check with delay to allow backend to start
    const initialDelay = setTimeout(() => {
      checkHealth();
    }, 1000);

    // If not healthy, retry more frequently initially
    const interval = setInterval(() => {
      if (!isHealthy && retryCount < 10) {
        setRetryCount(prev => prev + 1);
        checkHealth();
      } else if (isHealthy) {
        // Check every 30 seconds when healthy
        checkHealth();
      }
    }, isHealthy ? 30000 : 5000); // 5 seconds when unhealthy, 30 seconds when healthy

    return () => {
      clearTimeout(initialDelay);
      clearInterval(interval);
    };
  }, [isHealthy, retryCount]);

  return { isHealthy, isChecking, checkHealth, retryCount };
};
