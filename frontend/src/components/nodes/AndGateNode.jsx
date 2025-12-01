import React from 'react';
import { Handle, Position } from 'reactflow';

export default function AndGateNode({ data }) {
  return (
    <div style={{ position: 'relative' }}>
      {/* Input handles on the left */}
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
      
      {/* AND Gate SVG */}
      <svg width="80" height="60" viewBox="0 0 80 60">
        <path
          d="M 10,10 L 10,50 L 40,50 Q 60,50 60,30 Q 60,10 40,10 Z"
          fill="white"
          stroke="black"
          strokeWidth="2"
        />
      </svg>
      
      {/* Output handle on the right */}
      <Handle
        type="source"
        position={Position.Right}
        id="out"
        style={{ background: '#555' }}
      />
    </div>
  );
}
