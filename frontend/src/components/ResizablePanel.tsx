import React, { useState, useRef, useEffect } from 'react';
import './ResizablePanel.css';

interface ResizablePanelProps {
  left: React.ReactNode;
  right: React.ReactNode;
  defaultLeftWidth?: number;
  minLeftWidth?: number;
  minRightWidth?: number;
}

export const ResizablePanel: React.FC<ResizablePanelProps> = ({
  left,
  right,
  defaultLeftWidth = 300,
  minLeftWidth = 200,
  minRightWidth = 200,
}) => {
  const [leftWidth, setLeftWidth] = useState(defaultLeftWidth);
  const [isResizing, setIsResizing] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const startXRef = useRef<number>(0);
  const startWidthRef = useRef<number>(0);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing || !containerRef.current) return;

      const containerWidth = containerRef.current.offsetWidth;
      const deltaX = e.clientX - startXRef.current;
      const newWidth = startWidthRef.current + deltaX;

      const clampedWidth = Math.max(
        minLeftWidth,
        Math.min(containerWidth - minRightWidth, newWidth)
      );

      setLeftWidth(clampedWidth);
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isResizing, minLeftWidth, minRightWidth]);

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
    startXRef.current = e.clientX;
    startWidthRef.current = leftWidth;
  };

  return (
    <div className="resizable-panel" ref={containerRef}>
      <div className="resizable-left" style={{ width: `${leftWidth}px`, minWidth: `${minLeftWidth}px` }}>
        {left}
      </div>
      <div
        className="resizable-handle"
        onMouseDown={handleMouseDown}
        role="separator"
        aria-label="Resize panels"
        aria-orientation="vertical"
      />
      <div className="resizable-right" style={{ flex: 1, minWidth: `${minRightWidth}px` }}>
        {right}
      </div>
    </div>
  );
};

