// EditableNode.js
import React from "react";
import { Handle, Position } from "reactflow";

function EditableNode({ id, data }) {
  const handleChange = (e) => {
    if (data.onChange) {
      data.onChange(id, { [e.target.name]: e.target.value });
    }
  };

  const renderContent = () => {
    switch (data.blockType) {
      case "start":
        return <strong>Старт</strong>;
      case "end":
        return <strong>Конец</strong>;
      case "message":
        return (
          <textarea
            name="label"
            value={data.label || ""}
            onChange={handleChange}
            placeholder="Введите текст сообщения"
            style={{ width: "100%" }}
          />
        );
      case "question":
        return (
          <textarea
            name="label"
            value={data.label || ""}
            onChange={handleChange}
            placeholder="Введите вопрос"
            style={{ width: "100%" }}
          />
        );
      case "command":
        return (
          <input
            type="text"
            name="label"
            value={data.label || ""}
            onChange={handleChange}
            placeholder="/команда"
            style={{ width: "100%" }}
          />
        );
      case "image":
        return (
          <input
            type="text"
            name="url"
            value={data.url || ""}
            onChange={handleChange}
            placeholder="URL картинки"
            style={{ width: "100%" }}
          />
        );
      case "gallery":
        return (
          <textarea
            name="images"
            value={(data.images || []).join("\n")}
            onChange={(e) => {
              if (data.onChange) {
                data.onChange(id, { images: e.target.value.split("\n") });
              }
            }}
            placeholder="Список URL (по одному в строке)"
            style={{ width: "100%" }}
          />
        );
      case "button":
        return (
          <textarea
            name="buttons"
            value={(data.buttons || []).map((b) => b.label).join("\n")}
            onChange={(e) => {
              if (data.onChange) {
                data.onChange(id, {
                  buttons: e.target.value
                    .split("\n")
                    .map((label) => ({ label }))
                    .filter((b) => b.label.trim() !== "")
                });
              }
            }}
            placeholder="Текст кнопок (каждая с новой строки)"
            style={{ width: "100%" }}
          />
        );
      case "condition":
        return (
          <input
            type="text"
            name="condition"
            value={data.condition || ""}
            onChange={handleChange}
            placeholder="Введите условие"
            style={{ width: "100%" }}
          />
        );
      case "input":
        return (
          <input
            type="text"
            name="variableName"
            value={data.variableName || ""}
            onChange={handleChange}
            placeholder="Имя переменной"
            style={{ width: "100%" }}
          />
        );
      case "api":
        return (
          <div>
            <input
              type="text"
              name="url"
              value={data.url || ""}
              onChange={handleChange}
              placeholder="API URL"
              style={{ width: "100%", marginBottom: "4px" }}
            />
            <select
              name="method"
              value={data.method || "GET"}
              onChange={handleChange}
              style={{ width: "100%" }}
            >
              <option value="GET">GET</option>
              <option value="POST">POST</option>
              <option value="PUT">PUT</option>
              <option value="DELETE">DELETE</option>
            </select>
          </div>
        );
      default:
        return <span style={{ color: "red" }}>Неизвестный блок</span>;
    }
  };

  return (
    <div style={{ padding: 10, border: "1px solid #888", borderRadius: 5, background: "#fff", minWidth: 120 }}>
      {renderContent()}
      <Handle type="target" position={Position.Top} />
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

export default EditableNode;
