// ...existing code...
import React from 'react';
import { Handle, Position } from 'reactflow';

export default function InputNode({ data }) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '8px',
      border: 'none',
      borderRadius: '10px',
      background: 'transparent',
      color: '#ffffff',
      fontFamily: '"Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
      minWidth: '140px',
      minHeight: '64px',
      textAlign: 'center',
      position: 'relative',
    }}>
      {/* Label centered, decorative box removed */}
      <div style={{
        position: 'relative',
        zIndex: 2,
        fontWeight: 900,
        fontSize: '36px',
        letterSpacing: '0.6px',
        padding: '0 6px',
      }}>
        {data?.label ?? 'INPUT'}
      </div>

      <Handle
        type="source"
        position={Position.Right}
        style={{
          background: '#34d399',
          border: '2px solid #065f46',
          width: 16,
          height: 16,
          right: -8,
          top: '50%',
          transform: 'translateY(-50%)',
          zIndex: 3,
        }}
      />
    </div>
  );
}
// ...existing code...