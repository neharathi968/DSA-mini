import React from 'react';
import { Handle, Position } from 'reactflow';

export default function OrGateNode({ data }) {
  return (
    <div style={{ position: 'relative' }}>
      <Handle
        type="target"
        position={Position.Left}
        id="a"
        style={{ top: '30%', background: '#555' }}
      />
      <Handle
        type="target"
        position={Position.Left}
        id="b"
        style={{ top: '70%', background: '#555' }}
      />
      
      {/* OR Gate SVG */}
      <svg width="80" height="60" viewBox="0 0 80 60">
        <path
          d="M 10,10 Q 20,30 10,50 L 40,50 Q 65,50 70,30 Q 65,10 40,10 Z"
          fill="white"
          stroke="black"
          strokeWidth="2"
        />
        <path
          d="M 5,10 Q 10,30 5,50"
          fill="none"
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
