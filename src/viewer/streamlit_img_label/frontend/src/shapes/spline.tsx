import React from "react";
import { fabric } from "fabric"
import { SplinePoint, ShapeRenderProps } from "../interfaces";
import { sendSelectedShape } from "../streamlit-utils";

export const Spline: React.FC<ShapeRenderProps> = ({ shape, color = 'green', opacity = 0.3, canvas }) => {
  const { shapeType, points, label } = shape;

  let pathString = '';
  const firstPoint = new fabric.Point(points[0].x, points[0].y);

  pathString += `M${firstPoint.x},${firstPoint.y}`;

  for (let i = 1; i < points.length; i++) {
    const prevPoint = points[i - 1];
    const currPoint = points[i];
    const strokeWidth = (prevPoint as SplinePoint).r;

    pathString += `L${currPoint.x},${currPoint.y}`;
  }

  if (shapeType === "boundary") {
    color = "yellow"
  }

  const path = new fabric.Path(pathString, {
    stroke: color,
    fill: '',
    strokeWidth: 5,
    opacity,
  });

  const selectedPath = new fabric.Path(pathString, {
    stroke: color,
    fill: '',
    strokeWidth: 8,
    opacity,
    visible: false
  });

  canvas.add(path);
  canvas.add(selectedPath)

  path.on("mousedown", () => {
    canvas.discardActiveObject(); // Deselect any previously selected object
    console.log("selectedPath")
    if (selectedPath.visible) {
        // If the annotation is already selected, deselect it
        path.trigger("deselected"); // Manually trigger the deselected event
        selectedPath.visible = false;
    } else {
        // Otherwise, select the annotation
        selectedPath.set({visible: true});
        canvas.setActiveObject(selectedPath);
        path.trigger("selected"); // Manually trigger the selected event
    }
});

  path.on("mouseup", (event) => {
      if (!event.target) {
      // If no object is clicked, deselect any selected object
      const activeObject = canvas.getActiveObject();
      if (activeObject === selectedPath) {
          path.trigger("deselected"); // Manually trigger the deselected event
          selectedPath.visible = false;
      }
      }
  });

  // Add a click event listener to show the highlight rectangle
  path.on("selected", () => {
      selectedPath.set({visible: true});
      canvas.setActiveObject(selectedPath);

      console.log("selected " + shape)
      sendSelectedShape(shape)
  });

  // Add a click event listener to hide the highlight rectangle
  path.on("deselected", () => {
      selectedPath.visible = false;
  });

  const controlPoints = drawControlPoints(points as SplinePoint[], 'black')
  controlPoints.forEach(((point) => {
      canvas.add(point)
  }))

  return null;
};

function drawControlPoints(points: SplinePoint[], color: string = 'black'): fabric.Object[] {
    const controlPoints: fabric.Object[] = [];

  for (let i = 0; i < points.length; i++) {
      const x = points[i].x
      const y = points[i].y
      const x_offset = points[i].r;
      const line_x = new fabric.Line([x - x_offset, y, x + x_offset, y], {
          stroke: color,
          strokeWidth: 1,
      });

      controlPoints.push(line_x)
  }

  return controlPoints;
}