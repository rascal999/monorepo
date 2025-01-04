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
  const result = await pool.query(
    'INSERT INTO categories (name, slug, description) VALUES ($1, $2, $3) RETURNING id',
    [name, slug, description]
  );
  return result.rows[0].id;
}

async function createQuestion(categoryId, questionText) {
  const result = await pool.query(
    'INSERT INTO questions (category_id, question_text) VALUES ($1, $2) RETURNING id',
    [categoryId, questionText]
  );
  return result.rows[0].id;
}

async function createOption(questionId, optionText, isCorrect) {
  await pool.query(
    'INSERT INTO options (question_id, option_text, is_correct) VALUES ($1, $2, $3)',
    [questionId, optionText, isCorrect]
  );
}

async function migrateQuestions() {
  try {
    const questionsDir = path.join(process.cwd(), '..', 'public/questions/veterinary');
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
