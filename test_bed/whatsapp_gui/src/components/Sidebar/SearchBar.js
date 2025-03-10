import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';

/**
 * Search bar component for filtering chats and contacts
 */
const SearchBar = ({ onSearch }) => {
  const [query, setQuery] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = useRef(null);
  
  // Handle input change
  const handleChange = (e) => {
    const value = e.target.value;
    setQuery(value);
    onSearch(value);
  };
  
  // Handle clear button click
  const handleClear = () => {
    setQuery('');
    onSearch('');
    inputRef.current.focus();
  };
  
  // Focus input on keyboard shortcut (Ctrl+F)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        inputRef.current.focus();
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);
  
  return (
    <SearchContainer isFocused={isFocused}>
      <SearchIcon>🔍</SearchIcon>
      
      <SearchInput
        ref={inputRef}
        type="text"
        placeholder="Search chats or messages"
        value={query}
        onChange={handleChange}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
      />
      
      {query && (
        <ClearButton onClick={handleClear}>
          ✕
        </ClearButton>
      )}
    </SearchContainer>
  );
};

// Styled components
const SearchContainer = styled.div`
  display: flex;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: var(--color-surface-variant);
  border-radius: var(--border-radius-md);
  margin: var(--spacing-sm) var(--spacing-md);
  transition: box-shadow var(--transition-fast);
  box-shadow: ${props => 
    props.isFocused ? '0 0 0 2px var(--color-primary)' : 'none'};
`;

const SearchIcon = styled.span`
  font-size: var(--font-size-md);
  color: var(--color-text-secondary);
  margin-right: var(--spacing-sm);
`;

const SearchInput = styled.input`
  flex: 1;
  background: none;
  border: none;
  color: var(--color-text-primary);
  font-size: var(--font-size-md);
  padding: var(--spacing-xs) 0;
  
  &:focus {
    outline: none;
  }
  
  &::placeholder {
    color: var(--color-text-muted);
  }
`;

const ClearButton = styled.button`
  background: none;
  border: none;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  cursor: pointer;
  padding: var(--spacing-xs);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color var(--transition-fast);
  
  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
    color: var(--color-text-primary);
  }
`;

export default SearchBar;