export function QuizSearch({ searchTerm, onSearchChange, currentPage, totalPages, onPageChange }) {
  // Get current theme
  const isDarkMode = document.documentElement.getAttribute('data-theme') === 'dark';
  const searchInputStyle = {
    backgroundColor: isDarkMode ? '#2a2a3c' : '#ffffff',
    color: isDarkMode ? '#e6e6e6' : '#213547'
  };

  // Check if mobile view
  const isMobile = window.matchMedia('(max-width: 768px)').matches;

  return (
    <div className="search-box">
      <input
        type="text"
        className="search-input"
        placeholder="Search quizzes..."
        value={searchTerm}
        onChange={(e) => {
          onSearchChange(e.target.value);
        }}
        style={searchInputStyle}
      />
      {totalPages > 1 && (
        <div className="pagination">
          <button 
            className="pagination-btn"
            onClick={() => onPageChange(currentPage - 1)}
            disabled={currentPage === 1}
          >
            Previous
          </button>
          <span className="page-info">
            {isMobile ? `${currentPage} of ${totalPages}` : `Page ${currentPage} of ${totalPages}`}
          </span>
          <button 
            className="pagination-btn"
            onClick={() => onPageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
