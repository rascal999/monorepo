import { Handle, Position } from 'reactflow';

const CustomNode = ({ data }) => (
  <div className="text-center px-2 relative">
    <Handle type="target" position={Position.Top} />
    {data.label}
    <Handle type="source" position={Position.Bottom} />
  </div>
);

export default CustomNode;
