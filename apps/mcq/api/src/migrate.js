import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import pg from 'pg';
import dotenv from 'dotenv';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const pool = new pg.Pool({
  connectionString: process.env.DATABASE_URL
});

async function createCategory(name, slug, description = null) {
  try {
    // Try to find existing category first
    const existing = await pool.query(
      'SELECT id FROM categories WHERE slug = $1',
      [slug]
    );
    
    if (existing.rows.length > 0) {
      console.log(`Category ${name} already exists, skipping...`);
      return existing.rows[0].id;
    }

    // Create new category if it doesn't exist
    const result = await pool.query(
      'INSERT INTO categories (name, slug, description) VALUES ($1, $2, $3) RETURNING id',
      [name, slug, description]
    );
    return result.rows[0].id;
  } catch (err) {
    console.error(`Error creating category ${name}:`, err);
    throw err;
  }
}

async function createQuestion(categoryId, questionText) {
  try {
    // Try to find existing question first
    const existing = await pool.query(
      'SELECT id FROM questions WHERE category_id = $1 AND question_text = $2',
      [categoryId, questionText]
    );
    
    if (existing.rows.length > 0) {
      console.log(`Question already exists, skipping...`);
      return existing.rows[0].id;
    }

    // Create new question if it doesn't exist
    const result = await pool.query(
      'INSERT INTO questions (category_id, question_text) VALUES ($1, $2) RETURNING id',
      [categoryId, questionText]
    );
    return result.rows[0].id;
  } catch (err) {
    console.error(`Error creating question:`, err);
    throw err;
  }
}

async function createOption(questionId, optionText, isCorrect) {
  try {
    // Try to find existing option first
    const existing = await pool.query(
      'SELECT id FROM options WHERE question_id = $1 AND option_text = $2',
      [questionId, optionText]
    );
    
    if (existing.rows.length > 0) {
      console.log(`Option already exists, skipping...`);
      return;
    }

    // Create new option if it doesn't exist
    await pool.query(
      'INSERT INTO options (question_id, option_text, is_correct) VALUES ($1, $2, $3)',
      [questionId, optionText, isCorrect]
    );
  } catch (err) {
    console.error(`Error creating option:`, err);
    throw err;
  }
}

function getAllJsonFiles(dir) {
  let results = [];
  const list = fs.readdirSync(dir);
  
  for (const file of list) {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory()) {
      results = results.concat(getAllJsonFiles(filePath));
    } else if (file.endsWith('.json')) {
      results.push(filePath);
    }
  }
  
  return results;
}

async function migrateQuestions() {
  try {
    // Try Docker path first, then fallback to local path
    let publicDir;
    if (fs.existsSync('/app/public')) {
      publicDir = '/app/public';
    } else {
      publicDir = path.join(process.cwd(), '..', 'public');
    }

    const jsonFiles = getAllJsonFiles(publicDir);

    for (const filePath of jsonFiles) {
      const content = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      
      // Get relative path from public directory
      const relativePath = path.relative(publicDir, filePath);
      const pathParts = relativePath.split(path.sep);
      
      // Skip if not in questions directory
      if (pathParts[0] !== 'questions') continue;
      
      // Remove 'questions' from path and .json extension
      const categoryPath = pathParts.slice(1, -1).concat(pathParts.slice(-1)[0].replace('.json', ''));
      const categoryName = content.title || categoryPath.join(' - ').split('-').map(
        word => word.charAt(0).toUpperCase() + word.slice(1)
      ).join(' ');
      const categorySlug = categoryPath.join('-');
      
      console.log(`Migrating category: ${categoryName}`);
      const categoryId = await createCategory(categoryName, categorySlug);

      // Create questions and options
      for (const q of content.questions) {
        const questionId = await createQuestion(categoryId, q.question);
        
        for (let i = 0; i < q.options.length; i++) {
          await createOption(
            questionId,
            q.options[i],
            i === q.correctAnswer
          );
        }
      }
      
      console.log(`Completed migration for ${categoryName}`);
    }

    console.log('Migration completed successfully');
    process.exit(0);
  } catch (err) {
    console.error('Migration failed:', err);
    process.exit(1);
  }
}

// Run migration
migrateQuestions();
