export const controlPanelStyles = {
  panel: {
    position: "absolute",
    top: "10px",
    left: "50%",
    transform: "translateX(-50%)",
    display: "flex",
    alignItems: "center",
    gap: "8px",
    background: "white",
    padding: "10px 15px",
    borderRadius: "8px",
    boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
    zIndex: 1000,
    fontSize: "14px",
    flexWrap: "wrap",
    maxWidth: "90vw",
    overflowX: "auto"
  },
  button: {
    padding: "6px 10px",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
    fontSize: "12px",
    transition: "all 0.2s ease",
    minWidth: "40px"
  },
  primaryButton: {
    background: "#007bff",
    color: "white"
  },
  successButton: {
    background: "#28a745",
    color: "white"
  },
  dangerButton: {
    background: "#dc3545",
    color: "white"
  },
  warningButton: {
    background: "#ffc107",
    color: "black"
  },
  infoButton: {
    background: "#17a2b8",
    color: "white"
  },
  secondaryButton: {
    background: "#6c757d",
    color: "white"
  },
  dropdown: {
    position: "absolute",
    top: "100%",
    left: "50%",
    transform: "translateX(-50%)",
    background: "white",
    padding: "10px",
    borderRadius: "4px",
    boxShadow: "0 2px 10px rgba(0,0,0,0.2)",
    marginTop: "5px",
    zIndex: 1001,
    minWidth: "150px",
    fontSize: "12px"
  }
};

// Адаптивные стили для мобильных устройств
export const mobileControlPanelStyles = {
  panel: {
    position: "absolute",
    top: "10px",
    left: "10px",
    right: "10px",
    transform: "none",
    display: "flex",
    alignItems: "center",
    gap: "5px",
    background: "white",
    padding: "8px 10px",
    borderRadius: "8px",
    boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
    zIndex: 1000,
    fontSize: "12px",
    flexWrap: "wrap",
    maxWidth: "calc(100vw - 20px)",
    overflowX: "auto"
  },
  button: {
    padding: "4px 8px",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
    fontSize: "10px",
    transition: "all 0.2s ease",
    minWidth: "30px"
  },
  dropdown: {
    position: "absolute",
    top: "100%",
    left: "0",
    transform: "none",
    background: "white",
    padding: "8px",
    borderRadius: "4px",
    boxShadow: "0 2px 10px rgba(0,0,0,0.2)",
    marginTop: "5px",
    zIndex: 1001,
    minWidth: "120px",
    fontSize: "10px"
  }
};