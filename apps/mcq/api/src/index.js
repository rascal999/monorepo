import express from 'express';
import cors from 'cors';
import pg from 'pg';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const port = process.env.PORT || 3000;

// Create PostgreSQL pool
const pool = new pg.Pool({
  connectionString: process.env.DATABASE_URL
});

// Middleware
app.use(cors());
app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

// Get all categories
app.get('/api/categories', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM categories ORDER BY name');
    res.json(result.rows);
  } catch (err) {
    console.error('Error fetching categories:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get questions by category
app.get('/api/categories/:slug/questions', async (req, res) => {
  try {
    const { slug } = req.params;
    const result = await pool.query(
      `SELECT q.*, json_agg(json_build_object('id', o.id, 'text', o.option_text)) as options
       FROM questions q
       JOIN categories c ON q.category_id = c.id
       JOIN options o ON o.question_id = q.id
       WHERE c.slug = $1
       GROUP BY q.id`,
      [slug]
    );
    res.json(result.rows);
  } catch (err) {
    console.error('Error fetching questions:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get a single question with its options
app.get('/api/questions/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const result = await pool.query(
      `SELECT q.*, json_agg(json_build_object('id', o.id, 'text', o.option_text)) as options
       FROM questions q
       JOIN options o ON o.question_id = q.id
       WHERE q.id = $1
       GROUP BY q.id`,
      [id]
    );
    
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Question not found' });
    }
    
    res.json(result.rows[0]);
  } catch (err) {
    console.error('Error fetching question:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Start server
app.listen(port, () => {
  console.log(`API server running on port ${port}`);
});
