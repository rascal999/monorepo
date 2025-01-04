export const defaultEdgeOptions = {
  type: 'default',
  style: { 
    stroke: '#F472B6',
    strokeWidth: 3
  },
  animated: false
};

export const nodeColors = {
  default: {
    background: '#FCE7F3', // pink-100
    border: '#F472B6'      // pink-400
  },
  selected: {
    background: '#F9A8D4', // pink-300
    border: '#EC4899'      // pink-500
  }
};

export const nodeStyle = {
  width: 100,
  height: 100,
  borderRadius: '50%',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center'
};

export const edgeStyle = {
  stroke: '#F472B6',
  strokeWidth: 3
};

export const edgeMarker = {
  type: 'arrow',
  width: 20,
  height: 20,
  color: '#F472B6'
};
