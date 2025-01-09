import { useCallback, useRef } from 'react';
import { useDispatch } from 'react-redux';
import { NodeSingular } from 'cytoscape';
import { editNode } from '../store/slices/nodeSlice';
import { updateNodeInGraph } from '../store/slices/graphSlice';
import { colorOptions, ColorOption, defaultColors } from '../components/graph/GraphStyles';
import { NodeProperties } from '../store/types';

export const useNodeContextMenu = () => {
  const dispatch = useDispatch();
  const activeMenu = useRef<HTMLDivElement | null>(null);

  const removeMenu = useCallback(() => {
    if (activeMenu.current && document.body.contains(activeMenu.current)) {
      document.body.removeChild(activeMenu.current);
      activeMenu.current = null;
    }
  }, []);

  const handleContextMenu = useCallback((node: NodeSingular, event: MouseEvent) => {
    event.preventDefault();

    // Remove any existing menu
    removeMenu();

    // Create color menu
    const menu = document.createElement('div');
    menu.className = 'node-context-menu';
    menu.style.left = `${event.clientX}px`;
    menu.style.top = `${event.clientY}px`;
    activeMenu.current = menu;

    // Add color options
    colorOptions.forEach((color: ColorOption) => {
      const option = document.createElement('div');
      option.className = `menu-item${node.data('properties')?.color === color ? ' active' : ''}`;

      // Add color preview
      const preview = document.createElement('div');
      preview.className = `color-preview ${color}`;
      option.appendChild(preview);

      // Add color name
      const name = document.createElement('span');
      name.textContent = color.charAt(0).toUpperCase() + color.slice(1);
      option.appendChild(name);

      option.addEventListener('click', () => {
        // Get color scheme
        const scheme = defaultColors[color];

        // Create new properties object
        const properties: NodeProperties = {
          ...node.data('properties'),
          gradient: scheme.gradient,
          border: scheme.border,
          text: scheme.text,
          color
        };

        // Update node data in Cytoscape
        node.data('properties', properties);

        // Update node in Redux store
        const changes = {
          properties
        };

        // Update both node and graph slices
        dispatch(editNode({
          id: node.id(),
          changes
        }));

        dispatch(updateNodeInGraph({
          nodeId: node.id(),
          changes
        }));

        removeMenu();
      });

      menu.appendChild(option);
    });

    // Add click outside handler
    const handleClickOutside = (e: MouseEvent) => {
      if (!menu.contains(e.target as Node)) {
        removeMenu();
        document.removeEventListener('click', handleClickOutside);
        document.removeEventListener('keydown', handleKeyDown);
      }
    };

    // Add keydown handler for Escape key
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        removeMenu();
        document.removeEventListener('click', handleClickOutside);
        document.removeEventListener('keydown', handleKeyDown);
      }
    };

    document.addEventListener('click', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);
    document.body.appendChild(menu);
  }, [dispatch, removeMenu]);

  return handleContextMenu;
};
