import { QuizSearch } from './QuizSearch';
import { QuizItem } from './QuizItem';

export function QuizListSection({ title, files, isDirectoryFiles, onLoad, onDelete, searchTerm, onSearchChange, currentPage, onPageChange, itemsPerPage }) {
  const totalPages = Math.ceil(files.length / itemsPerPage);
  const paginatedFiles = files.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  return (
    <div className="quiz-section">
      <h2 className="section-title">{title}</h2>
      <QuizSearch
        searchTerm={searchTerm}
        onSearchChange={onSearchChange}
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={onPageChange}
      />
      <div className="files-list">
        {paginatedFiles.length > 0 ? (
          paginatedFiles.map(file => (
            <QuizItem
              key={file.id}
              file={file}
              isDirectoryFile={isDirectoryFiles}
              onLoad={onLoad}
              onDelete={onDelete}
            />
          ))
        ) : (
          <div className="no-results">No quizzes found matching "{searchTerm}"</div>
        )}
      </div>
    </div>
  );
}
