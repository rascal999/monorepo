import { useEffect, useState, useRef } from 'react';

export function Timer({ isRunning, onTick, showTimer = true }) {
  const [elapsedTime, setElapsedTime] = useState(0);
  const startTimeRef = useRef(null);
  const previousTimeRef = useRef(0);

  useEffect(() => {
    let intervalId;

    if (isRunning) {
      // Set initial start time if not set
      if (!startTimeRef.current) {
        startTimeRef.current = Date.now() - previousTimeRef.current;
      }

      intervalId = setInterval(() => {
        const currentElapsed = Date.now() - startTimeRef.current;
        setElapsedTime(currentElapsed);
        onTick(currentElapsed);
      }, 1000);
    } else {
      // Store the current elapsed time when stopping
      previousTimeRef.current = elapsedTime;
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [isRunning, onTick]);

  const formatDisplay = () => {
    const totalSeconds = Math.floor(elapsedTime / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };

  if (!showTimer) {
    return null;
  }

  return (
    <div className="timer">
      Time: <span>{formatDisplay()}</span>
    </div>
  );
}
