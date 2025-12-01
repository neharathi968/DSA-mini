import React from 'react';
import { Handle, Position } from 'reactflow';

export default function NotGateNode({ data }) {
  return (
    <div style={{ position: 'relative' }}>
      <Handle
        type="target"
        position={Position.Left}
        id="in"
        style={{ background: '#555' }}
      />
      
      {/* NOT Gate SVG (Triangle + Circle) */}
      <svg width="80" height="60" viewBox="0 0 80 60">
        <polygon
          points="10,10 10,50 55,30"
          fill="white"
          stroke="black"
          strokeWidth="2"
        />
        <circle
          cx="60"
          cy="30"
          r="5"
          fill="white"
          stroke="black"
          strokeWidth="2"
        />
      </svg>
      
      <Handle
        type="source"
        position={Position.Right}
        id="out"
        style={{ background: '#555' }}
      />
    </div>
  );
}
