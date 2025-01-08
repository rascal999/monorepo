import React from 'react';
import { useAppDispatch } from '../../store';
import { setError } from '../../store/slices/appSlice';
import { ActionTypes } from '../../store/types';

interface GraphToolbarProps {
  currentGraph: any;
  cyRef: React.MutableRefObject<any>;
  isInitializing: React.MutableRefObject<boolean>;
  onViewportUpdate: (viewport: { zoom: number; position: { x: number; y: number } }) => void;
}

const GraphToolbar: React.FC<GraphToolbarProps> = ({ 
  currentGraph, 
  cyRef, 
  isInitializing, 
  onViewportUpdate 
}) => {
  const dispatch = useAppDispatch();

  const handleImport = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const data = JSON.parse(e.target?.result as string);
          dispatch({ type: ActionTypes.IMPORT_GRAPH, payload: { data } });
        } catch (error) {
          dispatch(setError('Invalid graph file'));
        }
      };
      reader.readAsText(file);
    };
    input.click();
  };

  const handleExport = () => {
    if (!currentGraph) return;
    dispatch({ type: ActionTypes.EXPORT_GRAPH });
  };

  const handleResetView = () => {
    if (cyRef.current) {
      isInitializing.current = true;
      cyRef.current.fit();
      const newViewport = {
        zoom: cyRef.current.zoom(),
        position: {
          x: -cyRef.current.pan().x,
          y: -cyRef.current.pan().y
        }
      };
      onViewportUpdate(newViewport);
      isInitializing.current = false;
    }
  };

  return (
    <div className="toolbar">
      <button 
        className="button button-secondary"
        onClick={handleResetView}
      >
        Reset View
      </button>
      <button
        className="button button-secondary"
        onClick={handleImport}
      >
        Import
      </button>
      <button
        className="button button-secondary"
        onClick={handleExport}
        disabled={!currentGraph}
      >
        Export
      </button>
    </div>
  );
};

export default GraphToolbar;
