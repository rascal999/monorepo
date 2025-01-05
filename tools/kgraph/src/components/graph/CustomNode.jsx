import { Handle, Position } from 'reactflow';

const CustomNode = ({ data }) => (
  <div className={`text-center px-2 relative ${data.isLoading ? 'animate-pulse' : ''}`}>
    <Handle type="target" position={Position.Top} />
    <div className="flex items-center justify-center gap-2">
      {data.isLoading && (
        <div className="w-3 h-3 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      )}
      <span>{data.label}</span>
    </div>
    <Handle type="source" position={Position.Bottom} />
  </div>
);

export default CustomNode;
