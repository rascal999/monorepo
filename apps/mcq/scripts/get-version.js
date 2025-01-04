#!/usr/bin/env node

import { execSync } from 'child_process';
import { writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Get the latest mcq tag
try {
    const tag = execSync('git describe --tags --match "mcq/*" --abbrev=0', { encoding: 'utf8' }).trim();
    
    // Create or update .env.version file with full tag
    writeFileSync(
        join(__dirname, '..', '.env.version'),
        `VITE_APP_VERSION=${tag}\n`
    );
    
    console.log(`Version ${tag} saved to .env.version`);
} catch (error) {
    console.error('Error getting version:', error.message);
    // Fallback to development version if git tag not found
    writeFileSync(
        join(__dirname, '..', '.env.version'),
        'VITE_APP_VERSION=mcq/development\n'
    );
}
