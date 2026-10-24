import { useEffect } from "react";

export default function Toast({ message, error, actionText, onAction, onClose }) {
  useEffect(() => {
    const timer = setTimeout(onClose, 6000);
    return () => clearTimeout(timer);
  }, [onClose]);
  return (
    <div id="toast" role="status" className={error ? "error" : ""}>
      {message}
      {actionText && (
        <button onClick={() => { onClose(); onAction(); }}>{actionText}</button>
      )}
    </div>
  );
}
