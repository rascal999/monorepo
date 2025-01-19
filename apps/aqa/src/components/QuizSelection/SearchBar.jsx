import React from 'react';
import styles from './SearchBar.module.css';

const SearchBar = ({ 
  searchTerm, 
  setSearchTerm, 
  handleSearch, 
  fileInputRef, 
  handleFileUpload, 
  generating 
}) => {
  return (
    <div className={styles.container}>
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileUpload}
        accept=".txt,.pdf,.doc,.docx"
        className={styles.fileInput}
        disabled={generating}
      />
      <button
        onClick={() => fileInputRef.current?.click()}
        className={styles.uploadButton}
        disabled={generating}
      >
        Upload
      </button>
      <input
        type="text"
        placeholder="Search or enter a topic for a new quiz..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        className={styles.searchInput}
        disabled={generating}
      />
      <button 
        onClick={handleSearch}
        className={styles.searchButton}
        disabled={generating || !searchTerm.trim()}
      >
        {generating ? 'Generating Quiz...' : 'Search'}
      </button>
    </div>
  );
};

export default SearchBar;
