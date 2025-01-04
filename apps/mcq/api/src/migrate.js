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

async function migrateQuestions() {
  try {
    // Try Docker path first, then fallback to local path
    let questionsDir;
    if (fs.existsSync('/app/public/questions/veterinary')) {
      questionsDir = '/app/public/questions/veterinary';
    } else {
      questionsDir = path.join(process.cwd(), '..', 'public/questions/veterinary');
    }
    const files = fs.readdirSync(questionsDir);

    for (const file of files) {
      if (!file.endsWith('.json')) continue;

      const filePath = path.join(questionsDir, file);
      const content = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      
      // Create category from filename
      const categoryName = content.title || file.replace('.json', '').split('-').map(
        word => word.charAt(0).toUpperCase() + word.slice(1)
      ).join(' ');
      const categorySlug = file.replace('.json', '');
      
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
